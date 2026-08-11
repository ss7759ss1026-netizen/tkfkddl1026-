"""
매일 유튜브 플레이리스트 동향(인기 랭킹 TOP 10%, 트렌디한 플레이리스트, 관련 뉴스)을
수집해서 요약한 뒤 카카오톡 '나에게 보내기'로 전송한다.

필요한 환경 변수:
  YOUTUBE_API_KEY     Google Cloud에서 발급한 YouTube Data API v3 키
  KAKAO_REST_API_KEY  카카오 개발자 콘솔의 REST API 키
  KAKAO_REFRESH_TOKEN scripts/get_kakao_token.py로 최초 1회 발급받은 리프레시 토큰
  KAKAO_CLIENT_SECRET (선택) 카카오 앱에서 Client Secret을 활성화한 경우에만 설정

  GITHUB_TOKEN / GITHUB_REPOSITORY (선택, GitHub Actions에서 자동 제공)
    카카오가 리프레시 토큰을 재발급하면 GitHub Secrets(KAKAO_REFRESH_TOKEN)를
    자동으로 갱신한다. 이 저장소에 write 권한이 있는 토큰이 필요하다.
"""

from __future__ import annotations

import base64
import datetime as dt
import json
import os
import sys
import xml.etree.ElementTree as ET

import requests

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_MEMO_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
NEWS_RSS_URL = "https://news.google.com/rss/search"
YOUTUBE_TRENDING_LINK = "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D"

TOP_PERCENT = 0.1
KAKAO_TEXT_LIMIT = 200


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def fmt_views(count: str) -> str:
    try:
        n = int(count)
    except (TypeError, ValueError):
        return "조회수 알 수 없음"
    if n >= 100_000_000:
        return f"{n / 100_000_000:.1f}억회"
    if n >= 10_000:
        return f"{n / 10_000:.1f}만회"
    return f"{n:,}회"


def fetch_top_music_ranking(api_key: str) -> list[dict]:
    """한국 인기 음악 차트에서 상위 10% 랭킹을 가져온다."""
    resp = requests.get(
        f"{YOUTUBE_API_URL}/videos",
        params={
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "videoCategoryId": "10",  # Music
            "regionCode": "KR",
            "maxResults": 50,
            "key": api_key,
        },
        timeout=20,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    top_n = max(1, int(len(items) * TOP_PERCENT))
    ranking = []
    for item in items[:top_n]:
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        ranking.append(
            {
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "views": fmt_views(stats.get("viewCount")),
                "url": f"https://www.youtube.com/watch?v={item['id']}",
            }
        )
    return ranking


def fetch_trendy_playlists(api_key: str) -> list[dict]:
    """최근 7일 내 '플레이리스트' 관련 검색 결과 중 조회수 순위가 높은 영상."""
    published_after = (
        dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    resp = requests.get(
        f"{YOUTUBE_API_URL}/search",
        params={
            "part": "snippet",
            "q": "플레이리스트",
            "type": "video",
            "order": "viewCount",
            "regionCode": "KR",
            "relevanceLanguage": "ko",
            "publishedAfter": published_after,
            "maxResults": 10,
            "key": api_key,
        },
        timeout=20,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    playlists = []
    for item in items[:5]:
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]
        playlists.append(
            {
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
        )
    return playlists


def fetch_news(query: str = "유튜브 플레이리스트") -> list[dict]:
    params = {"q": query, "hl": "ko", "gl": "KR", "ceid": "KR:ko"}
    resp = requests.get(NEWS_RSS_URL, params=params, timeout=20)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    news = []
    for item in root.findall("./channel/item")[:5]:
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        news.append({"title": title, "url": link})
    return news


def build_sections(ranking, playlists, news) -> list[str]:
    today = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=9)  # KST
    date_str = today.strftime("%Y-%m-%d")

    sections = [f"📊 유튜브 플레이리스트 동향 요약 ({date_str})"]

    if ranking:
        lines = ["🔥 오늘의 인기 음악 랭킹 TOP (상위 10%)"]
        for i, v in enumerate(ranking[:5], start=1):
            lines.append(f"{i}. {v['title']} - {v['channel']} ({v['views']})")
        sections.append(truncate("\n".join(lines), KAKAO_TEXT_LIMIT))

    if playlists:
        lines = ["🎵 요즘 뜨는 플레이리스트"]
        for i, p in enumerate(playlists[:3], start=1):
            lines.append(f"{i}. {p['title']} - {p['channel']}")
        sections.append(truncate("\n".join(lines), KAKAO_TEXT_LIMIT))

    if news:
        lines = ["📰 관련 뉴스"]
        for i, n in enumerate(news[:3], start=1):
            lines.append(f"{i}. {n['title']}")
        sections.append(truncate("\n".join(lines), KAKAO_TEXT_LIMIT))

    return sections


def refresh_kakao_token(rest_api_key: str, refresh_token: str, client_secret: str | None) -> dict:
    data = {
        "grant_type": "refresh_token",
        "client_id": rest_api_key,
        "refresh_token": refresh_token,
    }
    if client_secret:
        data["client_secret"] = client_secret
    resp = requests.post(KAKAO_TOKEN_URL, data=data, timeout=20)
    resp.raise_for_status()
    return resp.json()


def send_kakao_text(access_token: str, text: str, link_url: str) -> None:
    template_object = {
        "object_type": "text",
        "text": text,
        "link": {"web_url": link_url, "mobile_web_url": link_url},
    }
    resp = requests.post(
        KAKAO_MEMO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        data={"template_object": json.dumps(template_object)},
        timeout=20,
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("result_code") != 0:
        raise RuntimeError(f"카카오 메시지 전송 실패: {result}")


def maybe_rotate_github_secret(new_refresh_token: str | None) -> None:
    """카카오가 새 refresh_token을 내려주면 GitHub Secrets(KAKAO_REFRESH_TOKEN)를 갱신한다."""
    if not new_refresh_token:
        return
    gh_token = os.environ.get("GH_SECRETS_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not gh_token or not repo:
        print("GH_SECRETS_TOKEN 또는 GITHUB_REPOSITORY가 없어 시크릿 자동 갱신을 건너뜁니다.", file=sys.stderr)
        return
    try:
        from nacl import encoding, public
    except ImportError:
        print("PyNaCl이 설치되지 않아 시크릿 자동 갱신을 건너뜁니다.", file=sys.stderr)
        return

    api = f"https://api.github.com/repos/{repo}/actions/secrets"
    headers = {
        "Authorization": f"Bearer {gh_token}",
        "Accept": "application/vnd.github+json",
    }
    key_resp = requests.get(f"{api}/public-key", headers=headers, timeout=20)
    key_resp.raise_for_status()
    key_data = key_resp.json()

    public_key = public.PublicKey(key_data["key"].encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(new_refresh_token.encode("utf-8"))
    encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")

    put_resp = requests.put(
        f"{api}/KAKAO_REFRESH_TOKEN",
        headers=headers,
        json={"encrypted_value": encrypted_b64, "key_id": key_data["key_id"]},
        timeout=20,
    )
    put_resp.raise_for_status()
    print("KAKAO_REFRESH_TOKEN 시크릿을 새 값으로 갱신했습니다.")


def main() -> int:
    youtube_key = os.environ["YOUTUBE_API_KEY"]
    kakao_rest_key = os.environ["KAKAO_REST_API_KEY"]
    kakao_refresh_token = os.environ["KAKAO_REFRESH_TOKEN"]
    kakao_client_secret = os.environ.get("KAKAO_CLIENT_SECRET")

    ranking, playlists, news = [], [], []

    try:
        ranking = fetch_top_music_ranking(youtube_key)
    except Exception as exc:  # noqa: BLE001
        print(f"인기 랭킹 수집 실패: {exc}", file=sys.stderr)

    try:
        playlists = fetch_trendy_playlists(youtube_key)
    except Exception as exc:  # noqa: BLE001
        print(f"플레이리스트 수집 실패: {exc}", file=sys.stderr)

    try:
        news = fetch_news()
    except Exception as exc:  # noqa: BLE001
        print(f"뉴스 수집 실패: {exc}", file=sys.stderr)

    if not (ranking or playlists or news):
        print("수집된 데이터가 없어 메시지를 보내지 않습니다.", file=sys.stderr)
        return 1

    sections = build_sections(ranking, playlists, news)

    token_data = refresh_kakao_token(kakao_rest_key, kakao_refresh_token, kakao_client_secret)
    access_token = token_data["access_token"]

    for section in sections:
        send_kakao_text(access_token, section, YOUTUBE_TRENDING_LINK)

    print(f"카카오톡 메시지 {len(sections)}건 전송 완료")

    maybe_rotate_github_secret(token_data.get("refresh_token"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
