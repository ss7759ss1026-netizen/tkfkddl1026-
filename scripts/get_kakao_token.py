"""
카카오톡 '나에게 보내기' 권한을 위한 리프레시 토큰을 최초 1회 발급받는 스크립트.

사전 준비 (카카오 개발자 콘솔 https://developers.kakao.com):
  1. 애플리케이션 추가 후 [앱 키] 메뉴에서 REST API 키를 확인한다.
  2. [카카오 로그인] 메뉴에서 활성화 설정을 ON으로 바꾼다.
  3. [카카오 로그인 > Redirect URI]에 아래 REDIRECT_URI 값을 그대로 등록한다.
     (예: https://localhost:3000 — 실제로 그 주소가 열릴 필요는 없다)
  4. [카카오 로그인 > 동의항목]에서 "카카오톡 메시지 전송"(talk_message)을
     선택 동의 또는 필수 동의로 설정한다.

사용법:
  YOUTUBE_API_KEY 등은 필요 없고, 아래 두 값만 직접 입력해서 실행한다.
    python scripts/get_kakao_token.py

  1) 터미널에 출력되는 인가 URL을 브라우저로 연다.
  2) 카카오 계정으로 로그인 후 동의하면 REDIRECT_URI로 리다이렉트되며
     페이지 자체는 열리지 않아도 된다 (에러 페이지가 떠도 정상).
  3) 그 주소창 URL 전체(또는 code= 뒤의 값)를 복사해서 터미널에 붙여넣는다.
  4) 출력된 refresh_token 값을 GitHub 저장소 Secrets에
     KAKAO_REFRESH_TOKEN 이름으로 등록한다.
"""

from __future__ import annotations

import urllib.parse

import requests

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
REDIRECT_URI = "https://localhost:3000"


def extract_code(user_input: str) -> str:
    user_input = user_input.strip()
    if user_input.startswith("http"):
        query = urllib.parse.urlparse(user_input).query
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            return params["code"][0]
        raise ValueError("입력한 URL에서 code 파라미터를 찾지 못했습니다.")
    return user_input


def main() -> None:
    rest_api_key = input("카카오 REST API 키를 입력하세요: ").strip()
    client_secret = input("Client Secret (사용 안 하면 그냥 엔터): ").strip() or None

    auth_url = KAKAO_AUTH_URL + "?" + urllib.parse.urlencode(
        {
            "client_id": rest_api_key,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "talk_message",
        }
    )
    print("\n아래 URL을 브라우저로 열어 로그인/동의를 진행하세요:\n")
    print(auth_url)
    print()

    raw = input("리다이렉트된 URL(또는 code 값)을 붙여넣으세요: ")
    code = extract_code(raw)

    data = {
        "grant_type": "authorization_code",
        "client_id": rest_api_key,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    if client_secret:
        data["client_secret"] = client_secret

    resp = requests.post(KAKAO_TOKEN_URL, data=data, timeout=20)
    resp.raise_for_status()
    token_data = resp.json()

    print("\n토큰 발급 성공\n")
    print(f"access_token  : {token_data['access_token']}")
    print(f"refresh_token : {token_data['refresh_token']}")
    print(
        "\n위 refresh_token 값을 GitHub 저장소 Settings > Secrets and variables "
        "> Actions 에서 KAKAO_REFRESH_TOKEN 이름으로 등록하세요."
    )


if __name__ == "__main__":
    main()
