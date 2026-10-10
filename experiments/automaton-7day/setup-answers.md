# `--setup` / `--configure` 입력 답안지

Conway Automaton **v0.2.1** 소스(`src/setup/wizard.ts`, `src/setup/configure.ts`,
`src/agent/policy-rules/financial.ts`, `src/conway/topup.ts`)를 직접 읽고 만든 답안지다.
버전이 다르면 질문 순서가 바뀔 수 있으니, 다르면 멈추고 확인한다.

모든 명령은 **Ubuntu(WSL) 창**, `~/automaton` 폴더에서 실행한다.

---

## A. `node dist/index.js --setup` (설정 마법사)

`--setup`은 설정만 저장하고 **종료한다** (에이전트를 켜지 않음 — `src/index.ts`에서 확인).
단, 2단계에서 Conway 서버에 지갑 서명으로 로그인해 API 키를 받는다 (돈은 움직이지 않음).

| 순서 | 화면에 나오는 질문 | 입력 | 이유 |
|---|---|---|---|
| 1/6 | `Chain type (evm or solana) [evm]` | **그냥 Enter** | 크레딧 구매(x402)는 EVM(Base)만 지원. 기존 지갑이 그대로 로드됨 (`Wallet loaded: 0x…`) |
| 2/6 | (자동) `Provisioning Conway API key (SIWE)...` | 없음 | 실패해서 키를 물으면 **그냥 Enter**로 건너뛰고 멈춘 뒤 확인 |
| 3/6 | `What do you want to name your automaton?` | `samdadora-lab-01` | 콘텐츠에서 부를 이름 |
| 3/6 | `Enter the genesis prompt` | `genesis-prompt.md`의 블록 붙여 넣기 → **Enter 두 번** | |
| 3/6 | `Creator wallet address (0x...)` | **주인 지갑 주소** (오토마톤 주소 아님!) | 감사 권한을 가진 사람 표시 |
| 3/6 | `OpenAI API key` | **그냥 Enter** | 외부 키를 넣으면 5달러 밖에서 돈이 샐 수 있음 |
| 3/6 | `Anthropic API key` | **그냥 Enter** | 위와 동일 |
| 3/6 | `Ollama base URL` | **그냥 Enter** | |

### Financial Safety Policy (단위: **센트**, 100 = 1달러)

코드상 판정은 `금액 > 한도`이면 거부다. 따라서 **0 = 전부 거부**.

| 질문 | 기본값 | 입력 | 의미 |
|---|---|---|---|
| `Max single transfer (cents)` | 5000 | **0** | 다른 주소로 송금 전면 차단 |
| `Max hourly transfers (cents)` | 10000 | **0** | 동일 |
| `Max daily transfers (cents)` | 25000 | **0** | 동일 |
| `Minimum reserve (cents)` | 1000 | **0** | 송금 자체가 막혀 있으므로 의미 없음 |
| `Max x402 payment (cents)` | 100 | **500** | 크레딧 최소 구매 단위 $5를 막지 않기 위함 (허용 도메인은 `conway.tech`만) |
| `Max daily inference spend (cents)` | 50000 | **100** | AI 사고 비용 하루 $1 상한 → 7일 ≈ $5와 맞물림 |
| `Require confirmation above (cents)` | 1000 | **0** | 모든 송금 시도는 격리·확인 대상 |

마지막에 `[6/6] Funding` 안내 상자가 나오고 프로그램이 끝난다. **아직 충전하지 않는다.**

---

## B. `node dist/index.js --configure` (마법사가 묻지 않는 항목)

메뉴에서 숫자를 고른다.

1. **`4` (General)**
   - `Agent name` → Enter
   - `Log level` → Enter (info)
   - `Max child automatons` → **0**
   - `Social relay URL` → Enter
   - `RPC endpoint` → Enter
2. **`2` (Model strategy)**
   - 모델 목록이 나오면 **가장 저렴한 모델**을 고른다 (fallback 두 개도 동일하게 저렴한 것)
   - `Max tokens per turn` → Enter
   - `Hourly inference budget (cents, 0 = unlimited)` → **10**
   - `Session inference budget (cents, 0 = unlimited)` → **500**
   - `Per-call ceiling (cents, 0 = unlimited)` → **5**
   - `Enable model fallback` → Enter
   - ⚠️ 이 메뉴에서는 **0이 "무제한"**이다. 0을 넣지 말 것.
3. **`q`** 로 종료

---

## C. 확인 명령

```bash
node dist/index.js --status
```

확인할 줄:
- `Name: samdadora-lab-01`
- `Address:` = 오토마톤 지갑 주소
- `Creator:` = 주인 지갑 주소 (두 주소가 **달라야** 함)
- `Children: 0 alive / 0 total`

설정 파일 위치: `~/.automaton/automaton.json` (API 키가 들어 있으므로 공유 금지).
