# SONG-INDEX

SAMDADORA × LUON SONG PRODUCTION GUIDE v2.0의 GATE CHECK(3-2 COLLISION)·
A/B/C 차별화(7-1)·PLAYLIST LAYER(4-1) 판정에 쓰는 곡 데이터 표.
새 곡을 승인할 때마다 맨 아래에 한 줄 추가한다. 상세 설계는 각 곡의
`catalog/YYYY-MM-###-song-slug.md` 마스터카드를 참고.

이 표는 v2.0 가이드 도입(2026-10-02) 이전에 설계된 6곡을 소급 정리한
것이다 — 당시에는 v2.0의 섹션 태그 규칙(5-6 SUNO LYRICS SAFETY GATE)·
가사 분량 120–130 words(5-4)가 아직 적용되지 않았으므로, 이 곡들의
가사 원문은 각 마스터카드에 기록된 그대로 두고 소급 재작업하지 않는다.
신규 곡부터 v2.0 전체 규칙을 적용한다.

| # | Song ID | Title | Core Line (핵심어) | 주요 이미지 | Hook 위치 | Groove Leader | Vocal 페르소나 | 주악기/Signature | BPM | 장르/무드 |
|---|---------|-------|---------------------|-------------|-----------|----------------|------------------|-------------------|-----|-----------|
| 1 | 2026-09-001 | Steady Light | "steady light" (반복·안정) | 카페 창가, 커피, 아침 | Chorus Open (D) | Guitar-led (fingerpicking→mute chop) | Soft natural male tenor | Vibraphone 3-note motif | 100 | Groove/Indie Pop, Café-Work |
| 2 | 2026-09-002 | Sail Slow | "sail slow" (느린 흐름) | 노을, 요트, 수평선 | Chorus Open (D) | Bass-led (rolling melodic) | Bright clear airy female | Tremolo guitar | 112 | Coastal Indie Pop, Drive |
| 3 | 2026-09-003 | Velvet Spotlight | "velvet spotlight" (무대·자기확신) | 재즈카페, 스포트라이트 | Chorus Open (D) | Keys-led (piano comping) | Warm textured low mezzo (breathy) | Piano motif + cymbal swell | 108 | Jazz-Pop/Neo-Soul, City Night |
| 4 | 2026-09-004 | Same Table | "same table" (가족·식탁) | 거실 바닥, 계란말이, 가족 | Chorus Open (D) | Percussion-led (heartbeat kick) | Male low intimate baritone | Guitar harmonics | 96 (justified deviation) | Acoustic Indie-Folk, Human Bonds |
| 5 | 2026-09-005 | New Ground | "new ground" (낯선 땅·자기발견) | 모래사막, 발자국, 홀로 | Chorus Open (D) | Guitar-led (motorik straight-eighth) | Bright youthful male tenor | Mono synth motif | 116 | Motorik Indie Pop, Travel |
| 6 | 2026-09-006 | Ancient Ground | "ancient ground" (고대의 땅·뿌리) | 모뉴먼트 밸리, 붉은 바위, 호간 | Chorus Open (D) | Bass-led (sustained drone) | Warm soft alto-mezzo | Slide guitar cry | 92 (justified deviation) | Desert Americana Folk, Human Bonds |

## COLLISION 참고 메모 (2026-10-02 기준)

- **Hook 위치**: 6곡 전부 Chorus Open(D)이다. v2.0 §4-5 HARD 규칙상
  "최근 3곡이 모두 D면 다른 위치를 쓴다" — **다음 곡부터는 Chorus
  Open(D) 외의 위치(B/C/E/G 등)를 반드시 검토할 것.**
- **CLICHÉ & TOURISM 단어(§3-2) 소급 체크**: New Ground가 "map",
  "blue"를, Ancient Ground가 "wind"를 포함함. v2.0 도입 이전 설계라
  소급 수정하지 않으나, 신규 곡에서는 동일 단어 재사용 시 GATE CHECK에서
  제거 검토 필요.
- **Groove Leader 분포**: Guitar-led ×2(1,5) / Bass-led ×2(2,6) /
  Keys-led ×1(3) / Percussion-led ×1(4). 다음 곡은 Keys-led 또는
  Percussion-led 재사용을 우선 피할 것.
- **Vocal 페르소나**: Male ×3(1,4,5) / Female ×3(2,3,6). 균형 상태.
- **Portfolio Class**: Light & Forward ×4(1,2,3,5) / Human Bonds
  ×2(4,6).

## COLLISION CHECK LOG (신규 곡 설계 시 기록)

| 신규 곡 | 비교 대상(최근 5곡) | 겹친 축 | 결과 |
|---------|----------------------|---------|------|
| Stay Instead / Pocket Town / Unhurried (MODE 2 A/B/C) | Sail Slow, Velvet Spotlight, Same Table, New Ground, Ancient Ground | 없음 | PASS |

## MODE 2 후보 — 바하라흐(독일) A/B/C (2026-10-02, PENDING — 오디오 미생성, SAMDADORA 선택 대기)

SONG-PRODUCTION-GUIDE-v2.0.md + SONG-CHECKLIST.md(우선 적용) 기준으로 설계.
가사 원문·스타일 프롬프트는 대화 기록 참고. 아래 세 곡 중 SAMDADORA가
고른 곡만 정식 카탈로그 번호(2026-10-00X)를 부여하고 실제 Suno 생성 후
QA를 진행한다.

| 후보 | Core Line | 주요 이미지 | Hook 위치 | Groove Leader | Vocal 페르소나 | 주악기/색채 | BPM | 시점 | 장르/무드 |
|---|---|---|---|---|---|---|---|---|---|
| A. Stay Instead | "I'm staying instead" | 와인마을 즉흥 축제, 놓친 비행기 | Chorus End ×2 | Accordion-led | Male lightly raspy tenor | Accordion + Handclaps | 118 | 1인칭 | Sunny Funk-Pop |
| B. Pocket Town | "you fit right in my pocket" | 손바닥만한 중세마을 | Chorus End ×2 | Mandolin-led | Female clear mezzo (hushed) | Mandolin + Glockenspiel | 104 | 2인칭 | Dreamy Indie Pop |
| C. Unhurried | "this town forgot to rush" | 중세 복장 축제, 멈춘 듯한 시간 | Chorus End ×2 | Vocal-rhythm-led (justified) | Male clear mature tenor | Bell keyboard chime + Tambourine | 88 (justified deviation) | 3인칭 | Slow Coastal Indie Folk |

**참고**: 세 곡 모두 Hook 위치가 Chorus End ×2로 동일함 —
`SONG-CHECKLIST.md`의 보편 구조 규칙(Tag 금지) 때문에 구조적으로
불가피했던 부분. `SONG-CHECKLIST.md` 하단 "추가 발견" 메모 참고.
