# PROJECT-LOG

SAMDADORA × LUON SONG PRODUCTION GUIDE v2.0이 지정하는 프로젝트 레벨
기록 파일. 개별 곡의 설계 디테일은 `catalog/*.md` 마스터카드에,
집계 데이터는 `catalog/SONG-INDEX.md`에 있다. 여기에는 시스템/워크플로
레벨 결정과 마일스톤만 기록한다.

## 2026-10-02 — SONG PRODUCTION GUIDE v2.0 도입

- SAMDADORA가 `SONG-PRODUCTION-GUIDE-v2.0.md`를 신규 작사·작곡
  파이프라인 표준으로 도입. 기존 `CLAUDE.md`(SAMDADORA × LUON UNIFIED
  CREATIVE & MUSIC OPERATING SYSTEM)는 유지되며, v2.0 가이드는 이를
  대체하지 않고 별도 문서로 공존한다 (OLD MASTER 보존 원칙).
- 신규 트래킹 파일 3종 생성: `catalog/SONG-INDEX.md`,
  `releases/PROJECT-LOG.md`(본 파일), `evidence/YOUTH-TEST-SERIES.md`.
- v2.0 도입 이전 설계된 6곡(Steady Light ~ Ancient Ground)은 소급
  재작업하지 않고 SONG-INDEX에 참고용으로 정리함. 신규 곡부터 v2.0
  전체 파이프라인(PART 3)·QA(PART 8)·출력 포맷(PART 9) 적용.
- 미해결 항목: "OLD MASTER(MUSIC-QA-MASTER-v7.0)"로 지칭되는 문서가
  이 저장소에 없음 — SAMDADORA가 별도로 보유한 문서로 추정. 필요 시
  첨부 요청.

## 2026-10-02 — SONG-CHECKLIST.md 추가 (v2.0 가이드와 일부 충돌)

- SAMDADORA가 1장짜리 실무 체크리스트(`SONG-CHECKLIST.md`)를 추가 지시.
  이 문서는 자체적으로 "전체 규칙은 CLAUDE.md"라고 명시 — 즉
  `SONG-PRODUCTION-GUIDE-v2.0.md`가 아니라 CLAUDE.md의 실무판으로
  제시됨.
- 세 문서(CLAUDE.md / SONG-PRODUCTION-GUIDE-v2.0.md / SONG-CHECKLIST.md)
  사이에 직접 충돌 발견: Tag 블록 허용 여부, 독립 악기 섹션 허용
  여부, 스타일 프롬프트 글자 수 한도(1,000 vs 950). CLAUDE.md §0
  CONFLICT PRIORITY(최신 명시적 결정 우선)에 따라 SONG-CHECKLIST.md
  쪽을 우선 적용하기로 하고, 충돌 내역은 `SONG-CHECKLIST.md` 하단에
  표로 기록함.
- 미해결: `yama_check.py`/`lyrics_check.py` 스크립트와 YAMA 판정
  기준(단어 목록)이 저장소에 없음 — SAMDADORA 확인/공유 필요. Voice
  ID 표기(M-01~M-10/F-01~F-08)가 기존 CLAUDE.md §38 보컬 슬롯과
  동일한 목록인지도 미확인. "배치" 단위 기준도 불명확 — 기존 6곡에는
  이 체크리스트의 배치 쿼터가 소급 적용되지 않음.

## 2026-10-02 — 첫 MODE 2 (A/B/C) 실행: 바하라흐 여행서적

- SAMDADORA가 독일 바하라흐(Bacharach) 여행서적 사진 5장 + 발췌 텍스트를
  주고 "A.B.C SONG" 요청 — v2.0 가이드 PART 2 MODE 2 최초 실행.
- 서로 다른 Human Truth 3개로 분리: A(계획을 깨고 머무는 용기) /
  B(작아도 완전한 것) / C(시간이 멈춘 듯한 장소 앞에서 서두름을 멈춤).
- SONG-CHECKLIST.md의 보편 구조 규칙(Tag 금지→훅 코러스 마지막행 2회
  반복)을 전부 적용하면서, v2.0 §7-1의 "A/B/C는 훅 위치도 반드시
  달라야 한다" 요구와 정면 충돌함을 발견 — 세 곡 모두 구조적으로
  Chorus End 위치가 될 수밖에 없음. 전달 방식(합창/속삭임/레가토)으로
  체감 차이만 만들고, 충돌 자체는 SONG-CHECKLIST.md에 기록, 투명하게
  보고함.
- 세 후보 모두 catalog/SONG-INDEX.md에 PENDING 상태로 기록. 아직 Suno
  생성 전 — SAMDADORA가 고른 곡만 정식 카탈로그 번호 부여 예정.

## 다음 액션

- 다음 신규 곡부터 Hook 위치를 Chorus Open(D) 외의 위치로 설계
  (SONG-INDEX COLLISION 메모 참고).
- 6곡 모두 Suno 생성 전(LISTENING QA: PENDING) 단계. 실제 오디오가
  들어오면 PART 8-2 기준으로 사람이 직접 판정 후 이 로그와
  `evidence/YOUTH-TEST-SERIES.md`에 결과 반영.
