# SAMDADORA Song Catalog Index

`catalog/` 아래에는 곡마다 하나의 Song Master Card + Rights & Release Log가
쌓인다. 새 곡을 시작할 때는 `_TEMPLATE_song-master-card.md`를 복사해
`YYYY-MM-###-song-slug.md`로 저장하고 채운다.

미확정 정보는 절대 추측하지 않고 `PENDING`, 오디오가 필요한 QA 항목은
`AUDIO REQUIRED`로 남긴다 (CLAUDE.md PART A §A12 참고).

## 파일

| Path | 용도 |
|---|---|
| `_TEMPLATE_song-master-card.md` | 빈 템플릿 — 새 곡마다 복사해서 사용 |
| `2026-09-001-steady-light.md` | 곡 #1 실제 카드 |
| `2026-09-002-sail-slow.md` | 곡 #2 실제 카드 |
| `2026-10-003-check-it-off.md` | 곡 #3 실제 카드 |
| `2026-10-004-between-stops.md` | 곡 #4 실제 카드 |

## 곡 목록

| Song ID | Title | Status | Portfolio Class | BPM | Vocal Slot | Design Score | Card |
|---|---|---|---|---|---|---|---|
| 2026-09-001 | Steady Light | DRAFT (HOLD — AUDIO) | LIGHT & FORWARD | 100 | 07 M soft natural tenor | 82/100 GOOD | [카드](2026-09-001-steady-light.md) |
| 2026-09-002 | Sail Slow | DRAFT (HOLD — AUDIO) | LIGHT & FORWARD | 112 | 01 F clear mezzo | 84/100 GOOD | [카드](2026-09-002-sail-slow.md) |
| 2026-10-003 | Check It Off | DRAFT (HOLD — AUDIO) | LIGHT & FORWARD | 116 | 03 M warm mid tenor-baritone | 86/100 DISTINCTIVE (추정) | [카드](2026-10-003-check-it-off.md) |
| 2026-10-004 | Between Stops | DRAFT (HOLD — AUDIO) | LIGHT & FORWARD | 104 | 05 F warm soft alto-mezzo | 85/100 DISTINCTIVE (추정) | [카드](2026-10-004-between-stops.md) |

## 카탈로그 스냅샷

- **감정 포트폴리오:** LIGHT & FORWARD 4 / HUMAN BONDS 0 (목표 70:30, 4곡 기준 아직 유의미한 비율 아님)
- **보컬 포트폴리오:** MALE SOLO 2 / FEMALE SOLO 2 / DUET 0 (목표 7:3:0)
- **BPM 분포:** 100, 104, 112, 116 (4곡, 100·104와 112·116이 각각 4 BPM 차로 근접 — 다음 곡은 106–110 구간 권장)
- **Groove Leader 분포:** GUITAR-LED 1 / BASS-LED 1 / PERCUSSION-LED 1 / DRUM-LED 1
- **브리지 패턴 주의:** 4곡 모두 서브트랙션(화성 악기 + 보컬만) — 다음 곡은 다른 브리지 방식 권장
- **오디오 QA 완료곡:** 0곡 (Sonic Dashboard 최소 목표 10곡 — 아직 활성화 전, CLAUDE.md PART B §57 참고)

이 스냅샷은 곡이 추가/갱신될 때마다 수동으로 업데이트한다. 10곡 이상 실제
오디오 QA 데이터가 쌓이면 CLAUDE.md PART B §57 SONIC DASHBOARD 기준의
전체 데이터 기반 대시보드로 전환한다.

## 다음 곡 추가 시 체크리스트

1. `_TEMPLATE_song-master-card.md`를 `YYYY-MM-###-song-slug.md`로 복사
2. SONG CREATION PIPELINE(CLAUDE.md PART B §17) 순서로 §1~7 채우기
3. 이 README의 "곡 목록" 표에 한 줄 추가
4. "카탈로그 스냅샷" 숫자 갱신
5. 오디오 생성 후 §9~14, §16~24 이어서 채우고 스냅샷 재갱신
