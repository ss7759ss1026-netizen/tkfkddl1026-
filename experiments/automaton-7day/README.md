# AUTOMATON 7-DAY EXPERIMENT — MASTER RUNBOOK (Windows / WSL)

> "잔고 5달러짜리 AI는 일주일 동안 무엇을 할까?"

OWNER: SAMDADORA · STATUS: READY TO EXECUTE · LAST UPDATED: 2026-10-10
RUNTIME: Conway Automaton v0.2.1 · ENV: Windows 표준 계정 + WSL Ubuntu + Node 22

## 0. 이 폴더의 파일

| 파일 | 용도 |
|---|---|
| `README.md` | 처음부터 끝까지 실행 순서 (이 문서) |
| `genesis-prompt.md` | 에이전트 첫 지시문 최종본 (붙여 넣기용) |
| `setup-answers.md` | `--setup` / `--configure` 질문별 입력값 |
| `experiment-log-template.md` | 사람이 쓰는 관찰 일지 (Day 0~8) |
| `content-plan.md` | 유튜브 / 인스타 / 블로그 콘텐츠 설계 |

## 1. 핵심 설계 원칙 (5줄)

1. **손실 상한 = 5 USDC.** 크레딧은 최소 $5 단위로만 살 수 있다(`TOPUP_TIERS = [5, …]`). 정확히 5 USDC만 넣으면 한 번 사고 끝이다.
2. **송금 0, 자식 0, 외부 AI 키 0.** 돈이 새는 세 갈래를 설정으로 막는다.
3. **지시문은 부탁, 한도는 자물쇠.** genesis prompt보다 재무 한도와 충전 금액을 믿는다.
4. **비밀은 한 곳에만.** `wallet.json`·복구 문구·`automaton.json`(API 키)은 화면·채팅·클라우드에 절대 올리지 않는다.
5. **멈춤 버튼을 먼저 익힌다.** 켜기 전에 끄는 법부터 연습한다.

## 2. 진행 상황

```
[x] PHASE 1  윈도우 표준 계정 + WSL + 오토마톤 설치 + 지갑 생성
[ ] PHASE 2  지갑 백업
[ ] PHASE 3  주인 지갑 준비 + 5 USDC 마련
[ ] PHASE 4  설정 (--setup, --configure) + 리허설
[ ] PHASE 5  충전 → 실행 (Day 0)
[ ] PHASE 6  7일 관찰 (Day 1~7)
[ ] PHASE 7  종료 · 정리 · 콘텐츠화 (Day 8)
```

---

## PHASE 2. 지갑 백업 (10분)

**왜:** WSL을 지우거나 PC가 고장 나면 지갑도 사라진다. 백업이 없으면 복구 불가.

1. USB를 꽂고 파일 탐색기에서 드라이브 문자 확인 (예: `E:` → 리눅스에서 `/mnt/e`).
2. Ubuntu 창:
   ```bash
   ls /mnt/e
   ```
   목록이 안 보이면(`No such file`) 아래로 연결한다 (sudo — 우분투 내부만 변경):
   ```bash
   sudo mkdir -p /mnt/e && sudo mount -t drvfs E: /mnt/e
   ```
3. 복사:
   ```bash
   cp ~/.automaton/wallet.json /mnt/e/automaton-wallet-backup.json
   ls -la /mnt/e/automaton-wallet-backup.json
   ```
4. 암호화: Windows **Pro** → USB 우클릭 → **BitLocker 켜기**.
   Windows **Home** → BitLocker 불가 → USB 사본을 지우고 **비밀번호 관리자 보안 메모에 첨부**로 대체.
   (에디션 확인: 설정 → 시스템 → 정보)
5. 작업 표시줄 → 하드웨어 안전하게 제거 → 서랍 보관.

✅ 완료 조건: 백업본이 PC 밖 한 곳에 존재 · 내용은 한 번도 화면에 출력하지 않음.

---

## PHASE 3. 주인 지갑 + 5 USDC 준비 (30분~1일)

**주인 지갑** (휴대폰 권장, 실험용 계정에서 하지 않음)
1. 지갑 앱(MetaMask, Coinbase Wallet, Rabby 등)에서 **새 지갑** 생성.
2. 복구 문구 12/24단어 → **종이에 손으로** 적어 보관.
3. 내 주소(0x…) 복사 → `setup-answers.md`의 Creator 칸에 쓸 주소.

**5 USDC 마련**
- 필요한 것: **Base 네트워크의 USDC 5개** + 주인 지갑에서 보낼 때 쓸 **소량의 Base ETH(수수료)**.
- 거래소에서 출금할 때는 **네트워크를 반드시 "Base"로** 선택한다. 다른 네트워크(Ethereum, Polygon 등)로 보내면 오토마톤이 인식하지 못한다.
- 거래소에서 Base 출금이 안 되면, 먼저 주인 지갑으로 받은 뒤 지갑 앱에서 Base로 옮긴다.
- 수수료를 고려해 주인 지갑에 **5 USDC + 약간의 여유**를 둔다. 오토마톤에게는 **정확히 5 USDC**만 보낸다.

✅ 완료 조건: 주인 지갑에 Base USDC ≥ 5 · 서로 다른 0x 주소 2개(오토마톤 / 주인) 메모 완료.

---

## PHASE 4. 설정 + 리허설 (20분)

1. Ubuntu 창:
   ```bash
   cd ~/automaton
   node dist/index.js --setup
   ```
   → `setup-answers.md` **A** 표대로 입력.
2. ```bash
   node dist/index.js --configure
   ```
   → `setup-answers.md` **B** 대로 입력 (자식 0, 예산 상한, 최저가 모델).
3. ```bash
   node dist/index.js --status
   ```
   → `Creator`와 `Address`가 다른지, `Children: 0`인지 확인.
4. **멈춤 리허설 (충전 전, 잔고 0 상태에서)**
   ```bash
   node dist/index.js --run
   ```
   - 로그가 흐르기 시작하면 10~20초 관찰 → **`Ctrl + C`** 로 멈춘다.
   - 잔고가 0이라 아무것도 사지 못한다 (`Bootstrap topup skipped: USDC balance $0.00 below minimum tier` 류 메시지가 정상).
   - 안 멈추면 PowerShell에서 `wsl --shutdown` (리눅스 전체 즉시 종료).

✅ 완료 조건: 두 가지 멈춤 방법을 직접 한 번씩 성공.

---

## PHASE 5. 충전 → 실행 = Day 0 (30분)

순서가 중요하다. **켜기 전에 기록부터.**

1. `experiment-log-template.md`의 **Day 0 · 예측** 칸을 먼저 채운다 (며칠 버틸지, 돈을 어디에 쓸지).
2. 주인 지갑 → 오토마톤 주소로 **5 USDC (Base)** 전송.
3. 도착 확인: 브라우저에서 `https://basescan.org/address/<오토마톤주소>` → USDC 5 표시.
4. 화면 녹화 시작 (`Win + Alt + R`) — 주소는 보여도 되고, 파일 내용은 절대 찍지 않는다.
5. 실행:
   ```bash
   cd ~/automaton
   node dist/index.js --run
   ```
6. 첫 몇 분 안에 볼 것 (코드상 동작):
   - 크레딧이 $5 미만이고 USDC ≥ $5이면 **자동으로 $5 크레딧 구매** (`Bootstrap topup` 로그).
   - 첫 턴에 `~/experiment-log.md` 상단에 시작 잔액·날짜 기록 (genesis prompt 지시).
7. Ubuntu 창은 **닫지 말고** 최소화. 창을 닫거나 PC가 잠들면 에이전트도 멈춘다.
   - 설정 → 시스템 → 전원 → 절전 모드를 실험 기간 동안 **"안 함"**(전원 연결 시)으로.

✅ 완료 조건: `Bootstrap topup` 성공 로그 · `experiment-log.md` 생성 · Day 0 기록 완료.

---

## PHASE 6. 7일 관찰 루틴 (하루 10분)

**두 번째 Ubuntu 창**을 열어 관찰한다 (첫 창은 에이전트가 사용 중).

```bash
cd ~/automaton
node dist/index.js --status          # 상태, 턴 수, 자식 수
cat ~/experiment-log.md              # 에이전트가 쓴 일지 (안전: 지갑 파일 아님)
```
+ BaseScan에서 오토마톤 주소의 USDC 잔액 확인.

매일 `experiment-log-template.md`에 사람 관찰 기록.

### 🚨 즉시 멈춤 조건 (하나라도 해당하면 `Ctrl + C` → 필요 시 `wsl --shutdown`)

| 신호 | 확인 방법 |
|---|---|
| `Children:` 숫자가 0보다 큼 | `--status` |
| 오토마톤 주소에서 **다른 주소로 나간 거래** | BaseScan 거래 목록 |
| 도메인 등록·외부 공개·연락 시도 로그 | 실행 창 로그 |
| 자기 소스 수정·도구 설치 시도 | 로그, `--status`의 `Tools` 증가 |
| PC가 눈에 띄게 느려지거나 팬이 계속 돎 | 작업 관리자 |

멈춘 뒤에는 바로 다시 켜지 말고, 무슨 일이었는지 기록한 다음 LUON과 점검한다.

---

## PHASE 7. 종료 · 정리 (Day 8)

1. 에이전트가 스스로 멈췄든(20% 또는 7일), 7일이 지났든 → 실행 창에서 **`Ctrl + C`**.
2. 최종 기록:
   ```bash
   node dist/index.js --status
   cp ~/experiment-log.md ~/experiment-log-final.md
   ```
3. `experiment-log.md`를 Windows로 꺼내기 (콘텐츠 재료):
   ```bash
   cp ~/experiment-log-final.md /mnt/c/Users/<윈도우사용자명>/Desktop/
   ```
4. 남은 크레딧: 회수 방법은 확인되지 않았다 → **5달러는 실험비로 전액 소진**된다고 간주.
5. 지갑은 지우지 않는다. 백업은 계속 보관 (같은 지갑으로 후속 실험 가능).
6. 다시 켜지 않는다면 `~/automaton` 폴더는 그대로 두어도 된다 (돈과 무관).

---

## 3. 일정표

| 날 | 할 일 | 소요 |
|---|---|---|
| Day −2 | PHASE 2 백업 · PHASE 3 주인 지갑 | 40분 |
| Day −1 | 5 USDC 마련 · PHASE 4 설정·리허설 · 쇼츠 #1 촬영 | 1시간 |
| Day 0 | 예측 기록 → 충전 → 실행 | 30분 |
| Day 1~7 | 관찰 루틴 · 일지 · 쇼츠 데일리 | 하루 10~20분 |
| Day 8 | 종료 · 최종 기록 · 롱폼 편집 시작 | 1시간 |

## 4. 절대 규칙 (체크용)

- [ ] `cat ~/.automaton/wallet.json` 입력하지 않음
- [ ] `wallet.json` / 복구 문구 / `automaton.json` 을 채팅·클라우드·화면 녹화에 노출하지 않음
- [ ] 오토마톤에게 5 USDC 초과 전송하지 않음
- [ ] 외부 AI 키(OpenAI/Anthropic) 입력하지 않음
- [ ] 실험용 Windows 계정에 관리자 권한 주지 않음
- [ ] 멈춤 조건 발생 시 고민하지 않고 먼저 끈다

## 5. 근거 (FACT / INFERENCE 구분)

- **FACT (소스 확인):** 크레딧 구매 단위 $5부터, Base USDC + x402 · 시작 시 크레딧 < $5 & USDC ≥ $5면 $5 자동 구매 · `--setup`은 설정 후 종료 · 송금 한도는 `금액 > 한도`면 거부(0 = 전면 차단) · Model strategy 예산은 0 = 무제한 · 마법사는 자식 수를 묻지 않음(`--configure` General에서 설정).
- **INFERENCE:** 남은 크레딧 환불 불가 가능성 · 자식 수 0 설정이 모든 경로에서 강제되는지 불확실 → 그래서 충전액 자체를 5 USDC로 제한.
- **FACT (2026-10-10 클라우드 테스트):** 설치·빌드·`--version`(v0.2.1)·`--init`(0x 주소, configDir)·`wallet.json` 생성 검증 완료.
