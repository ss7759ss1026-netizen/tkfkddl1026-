# 유튜브 에이전트 스킬 11개 (yt-*)

출처: [Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill)
@ `a2feb21` (2026-09-16) · MIT (`LICENSE-youtube-agent-skill`). 원본 파일은 수정 없이 그대로
복사했다. 이 저장소에서 Claude Code를 열면 `/yt-*` 명령으로 바로 쓸 수 있다.

**쓰기까지만 한다. 판단과 업로드는 SAMDADORA가 한다.** ("Nothing gets published until you do it.")

## 내 말투 파일

모든 스킬은 쓰기 전에 `~/.claude/youtube/voice.md`를 읽는다. 이 저장소에서는
`youtube/voice.md`가 원본이다. 새 환경(새 클라우드 세션 포함)에서 처음 쓰기 전에 한 번:

```bash
mkdir -p ~/.claude/youtube && cp youtube/voice.md ~/.claude/youtube/voice.md
```

말투를 고칠 땐 `youtube/voice.md`를 고치고 커밋한 뒤 다시 복사한다.

## ⚠️ 한글 후킹 — `/yt-script` 부를 때 같이 붙일 한 줄

`hookscore.py`는 단어를 `[a-z0-9'%$.]`로만 센다. 한글 문장은 어떤 문장이든 낮은 점수
(WEAK)에 몰려서, 그대로 두면 엉뚱한 후킹을 고른다.

```
후킹은 한국어로 쓰고 점수는 영어로 옮긴 문장으로 매겨줘.
각 후킹 옆에 영어 문장과 점수를 같이 보여주고, 고른 두 개는 한국어로 다시 다듬어줘.
```

## 11개 한눈에

| 명령 | 넣는 것 | 받는 것 |
| --- | --- | --- |
| `/yt-script` | 아이디어 한 줄 | 후킹 5개 점수 → 위 2개 → 화면 표시가 붙은 대본 |
| `/yt-package` | 주제·제목 후보 | 제목+썸네일 한 쌍, 잘림·중복·모호 검사 |
| `/yt-edit` | 자막 파일(srt·vtt) | 빈 구간·군말·다시 찍은 곳 타임코드 표 |
| `/yt-comment` | 댓글 붙여넣기 | 질문·정정·칭찬·무시 4갈래, 답글 초안, 고정할 하나 |
| `/yt-plan` | 쓸 수 있는 시간·반쯤 만든 것 | 본편 하나·가벼운 한 편·쇼츠 셋 |
| `/yt-viral` | 채널별 영상 목록 | 채널 평소(중앙값) 대비 배수 상위 다섯·제목 공식 |
| `/yt-retention` | 시청 지속 내보내기 CSV | 앞부분 이탈·급경사 지점·고칠 것 |
| `/yt-shorts` | 긴 영상 자막 | 혼자 서는 20~55초 구간·새 첫 문장 |
| `/yt-seo` | 영상 내용 | 설명란·쓸 만한 태그·노릴 검색어 셋 |
| `/yt-chapters` | 자막 파일 | 유튜브 규칙(00:00 시작·3개 이상·10초 이상)을 통과한 챕터 |
| `/yt-audit` | 채널 주소 | 채널 전체 점검 → 고칠 것 딱 하나 |

시청 지속 파일: 스튜디오 → 영상 → 분석 → 참여도 → 시청 지속 그래프의 내려받기.

## 파이썬 도구 6개 (추가 설치 없음, Python 3)

```bash
python3 .claude/skills/yt-script/hookscore.py --hook "one line"
python3 .claude/skills/yt-package/title.py --title "..." --thumb "..."
python3 .claude/skills/yt-edit/deadair.py transcript.srt
python3 .claude/skills/yt-chapters/chapters.py transcript.srt
python3 .claude/skills/yt-retention/retention.py retention.csv
python3 .claude/skills/yt-viral/swipe.py collected.json --min 2.0
```

## 알고 쓰기

- 후킹 점수 = 조회수 예측이 아니다. 74개 실제 후킹으로 맞춘 휴리스틱이라 "못 쓴 후킹"은
  잘 걸러내지만 같은 사람의 잘 된/안 된 영상은 거의 못 가른다.
- `/yt-viral`의 공식 이름은 제목 기준 판단일 뿐, 터진 이유가 아니다. 공개 목록만 읽는다.
- 없는 숫자는 지어내지 않는다 — 모르면 묻는다.
- 음악 제작(가사·Suno 프롬프트·QA)은 이 스킬이 아니라 `CLAUDE.md` PART A/B를 따른다.
  이 스킬은 플레이리스트 영상의 제목·썸네일·설명·쇼츠·댓글 쪽 원고 일을 맡는다.

## 업데이트

```bash
git clone --depth 1 https://github.com/Jakeschincariol/youtube-agent-skill.git /tmp/yas
cp -r /tmp/yas/skills/yt-* .claude/skills/
```
덮어쓰기 전에 원본 변경 내용을 읽어보고, 이 README의 커밋 해시를 갱신한다.
