"""
유튜브 음악·플레이리스트·관련 뉴스를 수집하여
카카오톡 '나에게 보내기'로 전송한다.
각 항목의 '원문 열기' 버튼으로 영상과 기사를 확인할 수 있다.

필수 환경 변수:
  YOUTUBE_API_KEY
  KAKAO_REST_API_KEY
  KAKAO_REFRESH_TOKEN

선택 환경 변수:
  KAKAO_CLIENT_SECRET
  GH_SECRETS_TOKEN
  GITHUB_REPOSITORY

카카오 제품 링크 관리에 등록할 도메인:
  https://www.youtube.com
  https://news.google.com
"""

from __future__ import annotations

import base64
import datetime as dt
import html
import json
import os
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_MEMO_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
NEWS_RSS_URL = "https://news.google.com/rss/search"
YOUTUBE_HOME = "https://www.youtube.com"
KST = dt.timezone(dt.timedelta(hours=9))
TOP_PERCENT = 0.1
TEXT_LIMIT = 200


def clean_text(value: str) -> str:
    return " ".join(html.unescape(value or "").split())


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit - 1].rstrip() + "…"


def fmt_views(count) -> str:
    try:
        number = int(count)
    except (TypeError, ValueError):
        return "조회수 알 수 없음"
    if number >= 100_000_000:
        return f"{number / 100_000_000:.1f}억회"
    if number >= 10_000:
        return f"{number / 10_000:.1f}만회"
    return f"{number:,}회"


def fetch_top_music_ranking(api_key: str) -> list[dict]:
    response = requests.get(
        f"{YOUTUBE_API_URL}/videos",
        params={
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "videoCategoryId": "10",
            "regionCode": "KR",
            "maxResults": 50,
            "key": api_key,
        },
        timeout=20,
    )
    response.raise_for_status()
    items = response.json().get("items", [])
    top_count = max(1, int(len(items) * TOP_PERCENT))
    result = []
    for item in items[:top_count]:
        snippet = item["snippet"]
        result.append({
            "title": clean_text(snippet["title"]),
            "channel": clean_text(snippet["channelTitle"]),
            "views": fmt_views(
                item.get("statistics", {}).get("viewCount")
            ),
            "url": f"https://www.youtube.com/watch?v={item['id']}",
        })
    return result


def fetch_trendy_playlists(api_key: str) -> list[dict]:
    published_after = (
        dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    response = requests.get(
        f"{YOUTUBE_API_URL}/search",
        params={
            "part": "snippet",
            "q": "음악 플레이리스트",
            "type": "video",
            "videoCategoryId": "10",
            "order": "viewCount",
            "regionCode": "KR",
            "relevanceLanguage": "ko",
            "publishedAfter": published_after,
            "maxResults": 25,
            "key": api_key,
        },
        timeout=20,
    )
    response.raise_for_status()
    result = []
    seen = set()
    excluded = ("뉴스", "속보", "긴급", "시사", "news", "breaking")
    for item in response.json().get("items", []):
        video_id = item["id"].get("videoId")
        snippet = item["snippet"]
        title = clean_text(snippet["title"])
        channel = clean_text(snippet["channelTitle"])
        if not video_id or video_id in seen:
            continue
        if any(word in f"{title} {channel}".lower() for word in excluded):
            continue
        seen.add(video_id)
        result.append({
            "title": title,
            "channel": channel,
            "url": f"https://www.youtube.com/watch?v={video_id}",
        })
        if len(result) == 3:
            break
    return result


def fetch_news() -> list[dict]:
    response = requests.get(
        NEWS_RSS_URL,
        params={
            "q": "유튜브 플레이리스트",
            "hl": "ko",
            "gl": "KR",
            "ceid": "KR:ko",
        },
        timeout=20,
    )
    response.raise_for_status()
    root = ET.fromstring(response.content)
    result = []
    seen = set()
    for item in root.findall("./channel/item"):
        title = clean_text(item.findtext("title") or "")
        link = (item.findtext("link") or "").strip()
        parsed = urlparse(link)
        if (
            not title
            or parsed.scheme != "https"
            or parsed.netloc != "news.google.com"
            or link in seen
        ):
            continue
        seen.add(link)
        result.append({"title": title, "url": link})
        if len(result) == 3:
            break
    return result


def build_messages(ranking, playlists, news) -> list[tuple[str, str]]:
    today = dt.datetime.now(KST).strftime("%Y-%m-%d")
    messages = [(
        f"📊 유튜브 음악 동향 ({today})\n"
        f"인기 음악 {len(ranking)}개 / "
        f"플레이리스트 {len(playlists)}개 / 뉴스 {len(news)}개\n"
        "각 메시지의 ‘원문 열기’를 눌러 확인하세요.\n"
        "인기 음악은 API 수집 결과의 상위 10%입니다.",
        YOUTUBE_HOME,
    )]
    groups = [
        ("🔥 한국 인기 음악", ranking),
        ("🎵 최근 7일 음악 플레이리스트", playlists),
        ("📰 플레이리스트 관련 뉴스", news),
    ]
    for heading, items in groups:
        for index, item in enumerate(items, start=1):
            lines = [f"{heading} · {index}", item["title"]]
            if item.get("channel"):
                lines.append(item["channel"])
            if item.get("views"):
                lines.append(item["views"])
            messages.append((
                truncate("\n".join(lines), TEXT_LIMIT),
                item["url"],
            ))
    return messages


def refresh_kakao_token(rest_key, refresh_token, client_secret) -> dict:
    data = {
        "grant_type": "refresh_token",
        "client_id": rest_key,
        "refresh_token": refresh_token,
    }
    if client_secret:
        data["client_secret"] = client_secret
    response = requests.post(KAKAO_TOKEN_URL, data=data, timeout=20)
    response.raise_for_status()
    return response.json()


def send_kakao_text(access_token: str, text: str, url: str) -> None:
    template = {
        "object_type": "text",
        "text": truncate(text, TEXT_LIMIT),
        "link": {"web_url": url, "mobile_web_url": url},
        "button_title": "원문 열기",
    }
    response = requests.post(
        KAKAO_MEMO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        data={"template_object": json.dumps(template, ensure_ascii=False)},
        timeout=20,
    )
    response.raise_for_status()
    if response.json().get("result_code") != 0:
        raise RuntimeError("카카오 메시지 전송 실패")


def maybe_rotate_github_secret(new_token) -> None:
    if not new_token:
        return
    gh_token = os.environ.get("GH_SECRETS_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not gh_token or not repo:
        print(
            "새 리프레시 토큰이 발급됐지만 자동 저장 설정이 없습니다. "
            "토큰 갱신 설정을 확인하세요.",
            file=sys.stderr,
        )
        return

    from nacl import encoding, public

    api = f"https://api.github.com/repos/{repo}/actions/secrets"
    headers = {
        "Authorization": f"Bearer {gh_token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(
        f"{api}/public-key", headers=headers, timeout=20
    )
    response.raise_for_status()
    key_data = response.json()
    public_key = public.PublicKey(
        key_data["key"].encode("utf-8"), encoding.Base64Encoder()
    )
    encrypted = public.SealedBox(public_key).encrypt(
        new_token.encode("utf-8")
    )
    response = requests.put(
        f"{api}/KAKAO_REFRESH_TOKEN",
        headers=headers,
        json={
            "encrypted_value": base64.b64encode(encrypted).decode("utf-8"),
            "key_id": key_data["key_id"],
        },
        timeout=20,
    )
    response.raise_for_status()
    print("리프레시 토큰 자동 저장 완료")


def log_failure(label: str, error: Exception) -> None:
    if isinstance(error, requests.HTTPError):
        response = error.response
        status = response.status_code if response is not None else "UNKNOWN"
        detail = f"HTTP {status}"
    else:
        detail = type(error).__name__
    print(f"{label}: {detail}", file=sys.stderr)


def main() -> int:
    youtube_key = os.environ["YOUTUBE_API_KEY"]
    rest_key = os.environ["KAKAO_REST_API_KEY"]
    refresh_token = os.environ["KAKAO_REFRESH_TOKEN"]
    client_secret = os.environ.get("KAKAO_CLIENT_SECRET")
    results = []

    for label, fetch in [
        ("인기 음악", lambda: fetch_top_music_ranking(youtube_key)),
        ("플레이리스트", lambda: fetch_trendy_playlists(youtube_key)),
        ("뉴스", fetch_news),
    ]:
        try:
            results.append(fetch())
        except Exception as error:
            log_failure(f"{label} 수집 실패", error)
            results.append([])

    ranking, playlists, news = results
    print(
        f"수집 결과: 인기 음악 {len(ranking)}개 / "
        f"플레이리스트 {len(playlists)}개 / 뉴스 {len(news)}개"
    )
    if not any(results):
        print("수집된 데이터가 없어 전송하지 않습니다.", file=sys.stderr)
        return 1

    token_data = refresh_kakao_token(rest_key, refresh_token, client_secret)
    rotation_failed = False
    try:
        maybe_rotate_github_secret(token_data.get("refresh_token"))
    except Exception as error:
        log_failure("리프레시 토큰 자동 저장 실패", error)
        rotation_failed = True

    messages = build_messages(ranking, playlists, news)
    for index, (text, url) in enumerate(messages, start=1):
        send_kakao_text(token_data["access_token"], text, url)
        print(f"카카오톡 메시지 {index}/{len(messages)} 전송 완료")
    return 1 if rotation_failed else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        log_failure("실행 실패", error)
        raise SystemExit(1)
