# SAMDADORA 곡 제작 체크리스트 (1장)

> 전체 규칙은 CLAUDE.md. 이 문서는 곡 만들 때 옆에 두는 실무판.
> ADOPTED: 2026-10-02 (SAMDADORA 지시) — `SONG-PRODUCTION-GUIDE-v2.0.md`와
> 겹치는 항목이 있으며, CLAUDE.md §0 CONFLICT PRIORITY("SAMDADORA의 최신
> 명시적 결정"이 최우선)에 따라 **이 체크리스트가 더 최근 지시이므로 아래
> 충돌 항목에서는 이 문서가 우선 적용된다.** 상세는 하단 "⚠️ v2.0 가이드와의
> 충돌 메모" 참고.

## ① 만들기 전 — 배정

- [ ] YAMA 후보 → `python yama_check.py 단어` (BLOCK/WARNING/PASS)
- [ ] 보이스 ID 배정 — M-01~M-10 / F-01~F-08 중 **배치 내 미사용 ID**
- [ ] 색채 악기 **2종** + 진입 구간 지정 (배치 내 조합 중복 금지)
- [ ] 시점 결정 — 배치 10곡당 1인칭 4 : 2인칭 3 : 3인칭 3, 연속 중복 금지
- [ ] 제목 — She/Her 금지. ①1인칭 ②사물 ③상태 ④동사구 중 선택

## ② 쓰면서 — 구역별 유형 (배치 쿼터)

| 구역 | 유형 | 쿼터 |
|---|---|---|
| 1절 첫 행 | 시각 도입 | ≤3곡 |
| 프리코러스 | ①인식반전 ≤3 / ②긴장누적 ③시간압박 ④감각집중 ⑤타인발화 | |
| 코러스 | **고정은 2행뿐** (YAMA 2행·훅 8행) | 나머지 6행 매번 다르게 |
| 2절 | ①과거회상 ≤3 / ②현재확장 ③반례 ④미래투사 ⑤구체수치 ⑥타인시점 | |
| 브리지 | 현재사건 / 철학전환 ≤2 / 대사 / 신체감각 / 침묵 | 동일유형 ≤2 |
| 아웃트로 | ①정리형 ≤2 / ②훅회귀 ③다음장면 ④한문장 ⑤되돌림 | |

## ③ 구조 — 무이음

- [ ] 인트로 = 완전 가창 2행 (상황 + 태도), 0~3초 진입, 대사 금지
- [ ] 프리코러스 끝을 `and`로 열어 코러스로 넘김
- [ ] 독립 악기 섹션 금지 → `[Groove Turnaround — bass and drums continue]`
- [ ] Tag 블록 금지 → 훅을 코러스 마지막 행에 2회 반복
- [ ] 마침표 제거
- [ ] 아웃트로 = 밴드 히트 아닌 자연 해소

## ④ 프롬프트

- [ ] 950자 이하 — **len()으로 실측**
- [ ] `warm rounded bass` 포함 / `no bass`·`no upbeat` 금지
- [ ] 첼로는 Emotional 풀 전용, 코러스 한정
- [ ] 흐름 3구: continuous pulse / joined by fills·turnarounds·pickups /
      no silence before final
- [ ] 초과 시 압축 4원칙 (흐름 3구 통합 → fully melodic 삭제 → 제외
      최소화 → 형용사 축약)

## ⑤ 내보내기 전 — 검수

```
python lyrics_check.py song.txt
python yama_check.py <YAMA>
```

- [ ] 직전 3곡 코러스를 나란히 놓고 같은 위치 문형 비교
- [ ] 중복 발견 시 **왜 그 자리에서 재사용했는지 설명** 후 수정

## 금지 문구 (즉시 탈락)

let it be / clap on two and clap on four / Not the X, I mean the Y /
past·beside the door / thrive / step inside / beyond the norm /
both hands / Jeju

---

## ⚠️ v2.0 가이드와의 충돌 메모 (2026-10-02 기록)

이 체크리스트와 `SONG-PRODUCTION-GUIDE-v2.0.md`가 직접 충돌하는 항목.
CLAUDE.md §0 CONFLICT PRIORITY("최신 명시적 결정" 최우선)에 따라, 아래는
**이 체크리스트 쪽을 우선 적용**한다. v2.0 가이드 쪽 조항은 유지하되
이 체크리스트가 지정한 곡에는 적용하지 않는다.

| 항목 | v2.0 가이드 (SONG-PRODUCTION-GUIDE-v2.0.md) | 이 체크리스트 (우선 적용) |
|---|---|---|
| Tag 섹션 | `[Tag]` 블록 명시적 허용 (5-1 구조, 5-6 SAFETY GATE 허용 태그 목록) | Tag 블록 금지 — 훅을 코러스 마지막 행에 2회 반복 |
| 독립 악기 섹션 | `[Instrumental Break]` 명시적 허용 태그 | 독립 섹션 금지 — `[Groove Turnaround — bass and drums continue]`로 대체 (단, v2.0 §5-6의 "태그 뒤 설명 금지" 규칙과도 충돌 — 대시 뒤 설명이 들어간 형태이므로 Suno 가사 블록이 아니라 **Style Prompt 쪽에 지시로 넣는 형태**로 운용 필요) |
| 스타일 프롬프트 글자 수 | 1,000자 이하 | **950자 이하로 더 엄격하게 적용** |
| 보컬 ID 표기 | 숫자 슬롯(01–10) + CLAUDE.md §38–40 VOCAL BASE ROTATION 서술형 | `M-01~M-10` / `F-01~F-08` 코드 표기 |
| 섹션별 가사 분량/유형 규칙 | 없음 (단어 수 총량만 규정) | 구역별 유형 쿼터표(②) 신규 적용 |

**미해결 — SAMDADORA 확인 필요:**
1. `yama_check.py`, `lyrics_check.py` 스크립트가 저장소에 없음. YAMA가
   정확히 무엇을 검사하는 로직/단어 목록인지(BLOCK/WARNING/PASS 기준)
   알아야 스크립트를 만들 수 있음 — 기존에 쓰시던 파일이 있으면 공유
   부탁드림.
2. Voice ID `M-01~M-10`/`F-01~F-08`이 CLAUDE.md §38의 기존 10개 보컬
   슬롯(01 F clear mezzo … 10 M clear mature tenor)과 같은 목록을
   가리키는지, 아니면 별도의 새 보이스 뱅크인지 확인 필요.
3. "배치(batch)"의 기준 단위(몇 곡을 1배치로 보는지, 지금까지의 6곡이
   1배치에 포함되는지)가 명확하지 않음 — 현재 카탈로그 6곡에는 이
   체크리스트의 시점 비율·보이스 ID 배정·구역별 쿼터가 소급 적용되지
   않은 상태.

**추가 발견 (2026-10-02, 바하라흐 A/B/C 설계 중) — 훅 위치 충돌:**
`SONG-PRODUCTION-GUIDE-v2.0.md` §7-1은 MODE 2(A/B/C)에서 "보컬
페르소나·주악기·그루브·**훅 위치**"가 반드시 달라야 한다고 규정하는데,
이 체크리스트의 "Tag 블록 금지 → 훅을 코러스 마지막 행에 2회 반복"
규칙이 모든 곡에 보편 적용되면서 모든 곡의 훅 위치가 구조적으로
"Chorus End ×2"로 고정됨 — 즉 MODE 2 A/B/C 세 곡의 훅 위치가 항상
같아질 수밖에 없어 두 문서가 직접 충돌함. 바하라흐 A/B/C 설계에서는
훅 전달 방식(합창형/속삭임/레가토)으로 체감 차이를 만드는 선에서
타협했으나, 근본적으로는 SAMDADORA 확인이 필요한 항목.
