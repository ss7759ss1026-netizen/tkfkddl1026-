# 유튜브 플레이리스트 동향 데일리 요약봇

매일 아침 7시(KST)에 유튜브 인기 음악 랭킹(상위 10%), 요즘 뜨는 플레이리스트,
관련 뉴스를 자동으로 수집해서 요약한 뒤 카카오톡 **나에게 보내기**(나와의 채팅방)로
전송합니다. GitHub Actions가 매일 자동으로 실행하므로 별도 서버가 필요 없습니다.

## 동작 방식

1. GitHub Actions가 매일 07:00 KST에 `scripts/daily_summary.py`를 실행합니다.
2. YouTube Data API로 한국 인기 음악 차트 상위 10%, 최근 7일 내 화제의
   "플레이리스트" 영상을 가져옵니다.
3. Google 뉴스 RSS로 관련 뉴스 헤드라인을 가져옵니다.
4. 카카오 REST API로 위 내용을 요약해 카카오톡 나에게 보내기로 전송합니다.

## 사전 준비: API 키 발급

### 1) YouTube Data API 키

1. [Google Cloud Console](https://console.cloud.google.com/)에서 새 프로젝트를 만듭니다.
2. **API 및 서비스 > 라이브러리**에서 `YouTube Data API v3`를 검색해 사용 설정합니다.
3. **API 및 서비스 > 사용자 인증 정보 > 사용자 인증 정보 만들기 > API 키**로 키를 발급받습니다.
4. 이 값이 `YOUTUBE_API_KEY` 입니다.

### 2) 카카오 REST API 키 + 리프레시 토큰

1. [카카오 개발자 콘솔](https://developers.kakao.com/)에서 애플리케이션을 추가합니다.
2. **앱 키**에서 REST API 키를 확인합니다. 이 값이 `KAKAO_REST_API_KEY` 입니다.
3. **카카오 로그인**을 활성화하고, **Redirect URI**에 `https://localhost:3000`을 등록합니다.
4. **동의항목**에서 "카카오톡 메시지 전송"(`talk_message`)을 동의 항목으로 설정합니다.
   (나에게 보내기는 별도 비즈니스 심사 없이 앱 관리자 본인 계정으로 바로 사용할 수 있습니다.)
5. 로컬 환경에서 아래 스크립트를 한 번 실행해 리프레시 토큰을 발급받습니다.

   ```bash
   pip install requests
   python scripts/get_kakao_token.py
   ```

   안내에 따라 브라우저에서 로그인/동의하고, 리다이렉트된 URL을 붙여넣으면
   `refresh_token`이 출력됩니다. 이 값이 `KAKAO_REFRESH_TOKEN` 입니다.

## GitHub Secrets 등록

저장소 **Settings > Secrets and variables > Actions > New repository secret**에서
아래 값들을 등록합니다.

| Secret 이름            | 필수 | 설명                                                   |
| ----------------------- | ---- | ------------------------------------------------------ |
| `YOUTUBE_API_KEY`       | 필수 | 위에서 발급한 YouTube Data API 키                       |
| `KAKAO_REST_API_KEY`    | 필수 | 카카오 앱의 REST API 키                                 |
| `KAKAO_REFRESH_TOKEN`   | 필수 | `get_kakao_token.py`로 발급한 리프레시 토큰              |
| `KAKAO_CLIENT_SECRET`   | 선택 | 카카오 앱에서 Client Secret을 활성화한 경우에만 등록      |
| `GH_SECRETS_TOKEN`      | 선택 | 아래 "리프레시 토큰 자동 갱신" 참고                      |

## 리프레시 토큰 자동 갱신 (선택)

카카오 리프레시 토큰은 보통 60일 정도의 유효기간을 가지며, 만료가 가까워지면
토큰 갱신 응답에 새 리프레시 토큰이 함께 내려옵니다. 매일 실행되는 이 워크플로가
그 새 값을 자동으로 GitHub Secrets에 반영하게 하려면, **repo** 권한(Secrets 쓰기 가능)이
있는 [Fine-grained personal access token](https://github.com/settings/tokens?type=beta)을
만들어 `GH_SECRETS_TOKEN` 이름으로 등록하세요. 등록하지 않아도 매일 발송 자체는
정상 동작하며, 다만 리프레시 토큰이 만료되면(약 두 달 주기) `get_kakao_token.py`를
다시 한 번 실행해 `KAKAO_REFRESH_TOKEN`을 수동으로 갱신해야 합니다.

## 동작 확인

Secrets를 모두 등록한 뒤 **Actions 탭 > Daily YouTube Playlist Summary > Run workflow**로
수동 실행해서 카카오톡 나와의 채팅방에 메시지가 오는지 바로 확인할 수 있습니다.
매일 자동 실행은 `.github/workflows/daily-summary.yml`의 cron 스케줄(07:00 KST)에 따라
별도 조작 없이 계속됩니다.

## 발송 시간 변경

`.github/workflows/daily-summary.yml`의 `cron: "0 22 * * *"` (UTC 기준)을 원하는
시간에 맞게 수정하세요. KST는 UTC+9이므로, 예를 들어 오전 8시에 받고 싶다면
`0 23 * * *`로 바꾸면 됩니다.
