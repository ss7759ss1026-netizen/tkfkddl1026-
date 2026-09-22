"""
SAMDADORA JUDGE ENGINE v1.0

CLAUDE.md(SAMDADORA x LUON MUSIC OS v1.0 + PRODUCTION STANDARD v6.0/v6.1)를
Master Standard로 삼아, 곡 하나(JSON)를 HARD / ADVISORY / SOFT / CATALOG /
RELEASE 다섯 카테고리로 평가한다.

핵심 원칙 (CLAUDE.md PART A §A16 DECISION AND EVIDENCE RULES 반영):
  - 모든 수치는 실제로 계산한다. 추정해서 PASS 처리하지 않는다.
  - HARD 규칙 위반이 하나라도 있으면 verdict는 MASTER FAIL — HARD BLOCK이다.
  - HARD는 전부 통과했더라도 SOFT REPAIR / CATALOG REDESIGN / RELEASE FAIL
    (수리 필요 등급)이나 ADVISORY·CATALOG·RELEASE의 미해결 REVIEW(검수 필요
    등급)가 하나라도 남아 있으면 "MASTER READY"라고 표시하지 않는다 —
    각각 NEEDS REPAIR / NEEDS REVIEW로 명시한다.
  - MASTER READY는 모든 HARD PASS + 필수 REPAIR 없음(SOFT REPAIR/CATALOG
    REDESIGN/RELEASE FAIL 없음) + 미해결 REVIEW 없음(ADVISORY/CATALOG/
    RELEASE REVIEW 없음) 상태에서만 허용한다.
  - SOFT는 창작적/주관적 항목이라 기계적으로 PASS를 줄 수 없다.
    근거가 없으면 UNASSESSED, 결함이 발견되면 REPAIR만 반환한다.
  - CATALOG/RELEASE는 필요한 데이터가 없으면 INSUFFICIENT EVIDENCE /
    NOT APPLICABLE로 남기고 임의로 판단하지 않으며, 이 상태 자체는
    MASTER READY를 막지 않는다 — 다만 그것을 "검증 완료"로 승격하지도
    않는다 (검증되지 않은 채로 남아 있을 뿐이다).

이 모듈은 config/judge-rules.json에 정의된 규칙만 읽어서 실행한다.
규칙의 수치 자체를 이 파일에 하드코딩하지 않는다 (CLAUDE.md 갱신 시
judge-rules.json만 갱신하면 되도록).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_RULES_PATH = Path(__file__).resolve().parent.parent / "config" / "judge-rules.json"

STATUS_PASS = "PASS"
STATUS_REVIEW = "REVIEW"
STATUS_FAIL = "FAIL"
STATUS_REDESIGN = "REDESIGN"
STATUS_UNASSESSED = "UNASSESSED"
STATUS_REPAIR = "REPAIR"
STATUS_INSUFFICIENT_EVIDENCE = "INSUFFICIENT EVIDENCE"
STATUS_NOT_APPLICABLE = "NOT APPLICABLE"

VERDICT_HARD_BLOCK = "MASTER FAIL — HARD BLOCK"
VERDICT_NEEDS_REPAIR = "NEEDS REPAIR"
VERDICT_NEEDS_REVIEW = "NEEDS REVIEW"
VERDICT_MASTER_READY = "MASTER READY"


def load_rules(path: str | Path = DEFAULT_RULES_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Real measurement helpers (실제 계산 — 추정 금지)
# ---------------------------------------------------------------------------

def count_prompt_chars(prompt: str) -> int:
    """공백 포함 실제 문자 수. len() 그대로 사용하며 추정하지 않는다."""
    return len(prompt or "")


_SECTION_LABEL_RE = re.compile(r"\[[^\]]*\]")
_WORD_RE = re.compile(r"[^\s]+")


def count_sung_words(lyrics: str) -> int:
    """실제 sung word 수. [Verse 1] 같은 구조 라벨은 가사가 아니므로 제외한다."""
    if not lyrics:
        return 0
    stripped = _SECTION_LABEL_RE.sub(" ", lyrics)
    tokens = [t for t in _WORD_RE.findall(stripped) if re.search(r"[A-Za-z0-9가-힣]", t)]
    return len(tokens)


def extract_structure(song: dict, structure_cfg: dict) -> list[str]:
    """song['structure']가 있으면 그것을, 없으면 가사의 [Label] 순서를 사용한다."""
    raw: list[str]
    if song.get("structure"):
        raw = list(song["structure"])
    else:
        raw = _SECTION_LABEL_RE.findall(song.get("lyrics", ""))
        raw = [r.strip("[]") for r in raw]
    return _normalize_structure(raw, structure_cfg)


def _normalize_structure(raw_labels: list[str], structure_cfg: dict) -> list[str]:
    aliases = {k.lower(): v for k, v in structure_cfg.get("aliases", {}).items()}
    normalized: list[str] = []
    for raw in raw_labels:
        key = raw.strip().lower()
        if key in aliases:
            normalized.append(aliases[key])
            continue
        if "final" in key and "chorus" in key and "tag" in key:
            normalized.append("Final Chorus")
            normalized.append("Final Tag")
            continue
        normalized.append(raw.strip())
    return normalized


# ---------------------------------------------------------------------------
# Individual rule checks — each returns a result dict
# ---------------------------------------------------------------------------

def _result(rule: dict, status: str, **extra: Any) -> dict:
    out = {
        "id": rule["id"],
        "status": status,
        "source": rule.get("source", ""),
        "description": rule.get("description", ""),
    }
    out.update(extra)
    return out


def check_char_limit(song: dict, rule: dict) -> dict:
    prompt = song.get(rule["field"], "") or ""
    n = count_prompt_chars(prompt)
    limit = rule["max_chars"]
    status = STATUS_PASS if n <= limit else STATUS_FAIL
    return _result(rule, status, value=n, limit=limit)


def check_char_recommended_range(song: dict, rule: dict) -> dict:
    prompt = song.get(rule["field"], "") or ""
    n = count_prompt_chars(prompt)
    lo, hi = rule["min"], rule["max"]
    status = STATUS_PASS if lo <= n <= hi else STATUS_REVIEW
    return _result(rule, status, value=n, recommended_min=lo, recommended_max=hi)


def check_structure_required(song: dict, rule: dict, structure_cfg: dict) -> dict:
    structure = extract_structure(song, structure_cfg)
    required = structure_cfg["required_min_count"]
    counts: dict[str, int] = {}
    for label in structure:
        counts[label] = counts.get(label, 0) + 1

    missing = []
    for label, min_count in required.items():
        if counts.get(label, 0) < min_count:
            missing.append({"section": label, "required": min_count, "found": counts.get(label, 0)})

    status = STATUS_PASS if not missing else STATUS_FAIL
    return _result(
        rule,
        status,
        structure_found=structure,
        section_counts=counts,
        missing_required_sections=missing,
    )


def check_structure_order(song: dict, rule: dict, structure_cfg: dict) -> dict:
    structure = extract_structure(song, structure_cfg)
    first_index: dict[str, int] = {}
    for idx, label in enumerate(structure):
        if label not in first_index:
            first_index[label] = idx

    violations = []
    for a, b in structure_cfg.get("ordering_constraints", []):
        if a in first_index and b in first_index and first_index[a] >= first_index[b]:
            violations.append({"before": a, "after": b})

    status = STATUS_PASS if not violations else STATUS_REVIEW
    return _result(rule, status, order_violations=violations)


def check_bpm_range_with_justification(song: dict, rule: dict) -> dict:
    bpm = song.get(rule["field"])
    if bpm is None:
        return _result(rule, STATUS_UNASSESSED, reason="bpm 값이 song JSON에 없음")

    lo, hi = rule["min"], rule["max"]
    justification = (song.get(rule["justification_field"]) or "").strip()

    if lo <= bpm <= hi:
        return _result(rule, STATUS_PASS, value=bpm, range=[lo, hi])

    if justification:
        return _result(
            rule, STATUS_PASS, value=bpm, range=[lo, hi],
            note="JUSTIFIED DEVIATION", justification=justification,
        )

    return _result(
        rule, STATUS_REVIEW, value=bpm, range=[lo, hi],
        note="범위를 벗어났으나 음악적 근거(bpm_justification)가 제공되지 않음",
    )


def check_word_range_by_mood(song: dict, rule: dict) -> dict:
    lyrics = song.get(rule["field"], "") or ""
    n = count_sung_words(lyrics)

    mood = (song.get(rule["mood_field"]) or "").strip().lower()
    overrides = {k.lower(): v for k, v in rule.get("mood_overrides", {}).items()}
    lo, hi = overrides.get(mood, rule["default_range"])

    status = STATUS_PASS if lo <= n <= hi else STATUS_REVIEW
    return _result(
        rule, status, value=n, range=[lo, hi],
        mood=mood or "general", mood_exception_applied=mood in overrides,
    )


def check_avoid_terms(song: dict, rule: dict) -> dict:
    if rule.get("applies_when_genre_unspecified_only") and song.get(rule.get("genre_field", "genre")):
        return _result(rule, STATUS_NOT_APPLICABLE, reason="장르가 명시되어 기본값 회피 목록 미적용")

    text = " ".join(str(song.get(f, "") or "") for f in rule["fields"]).lower()
    found = [term for term in rule["terms"] if term.lower() in text]
    status = STATUS_PASS if not found else STATUS_REVIEW
    return _result(rule, status, matched_terms=found)


def check_forbidden_reference(song: dict, rule: dict) -> dict:
    text = " ".join(str(song.get(f, "") or "") for f in rule["fields"])
    lowered = text.lower()

    matched_names = [name for name in rule["blocklist_names"] if name.lower() in lowered]
    matched_patterns = [
        pat for pat in rule["reference_phrase_patterns"]
        if re.search(pat, text, flags=re.IGNORECASE)
    ]

    status = STATUS_FAIL if (matched_names or matched_patterns) else STATUS_PASS
    return _result(
        rule, status,
        matched_artist_names=matched_names,
        matched_reference_patterns=matched_patterns,
    )


def check_soft_field_presence(song: dict, rule: dict) -> dict:
    value = song.get(rule["field"])
    if not value or (isinstance(value, str) and not value.strip()):
        return _result(rule, STATUS_REPAIR, reason=f"{rule['field']} 필드가 비어 있음")
    return _result(
        rule, STATUS_UNASSESSED, value=value,
        reason="필드는 존재하나 창작적 품질은 자동 판정 불가 — LUON/SAMDADORA 검토 필요",
    )


def check_cliche_scan(song: dict, rule: dict) -> dict:
    lyrics = (song.get(rule["field"], "") or "").lower()
    found = [phrase for phrase in rule["cliche_phrases"] if phrase.lower() in lyrics]
    if found:
        return _result(rule, STATUS_REPAIR, matched_cliches=found)
    return _result(
        rule, STATUS_UNASSESSED,
        reason="알려진 클리셰 목록과 일치하는 문구는 없었으나, 참신함 자체는 자동 판정 불가",
    )


def check_requires_audio(song: dict, rule: dict) -> dict:
    if not song.get(rule["audio_field"]):
        return _result(rule, STATUS_UNASSESSED, reason="AUDIO REQUIRED — 실제 오디오 없이는 QA 불가")
    return _result(
        rule, STATUS_UNASSESSED,
        reason="오디오는 제공되었으나 실제 청취 판단은 LUON/SAMDADORA 영역 — 자동 PASS 불가",
    )


def check_recent5_overlap(song: dict, rule: dict) -> dict:
    catalog = song.get("catalog_context") or {}
    overlap = catalog.get(rule["catalog_field"])
    if overlap is None:
        return _result(rule, STATUS_INSUFFICIENT_EVIDENCE, reason="recent5_overlap_count 데이터 없음")

    pass_max = rule["thresholds"]["pass_max"]
    review_max = rule["thresholds"]["review_max"]
    if overlap <= pass_max:
        status = STATUS_PASS
    elif overlap <= review_max:
        status = STATUS_REVIEW
    else:
        status = STATUS_REDESIGN
    return _result(rule, status, overlap_count=overlap)


def check_vocal_portfolio(song: dict, rule: dict) -> dict:
    catalog = song.get("catalog_context") or {}
    counts = catalog.get(rule["catalog_field"])
    if not counts:
        return _result(rule, STATUS_INSUFFICIENT_EVIDENCE, reason="vocal_counts 데이터 없음")

    target = rule["target_ratio"]
    drift = {k: counts.get(k, 0) - target.get(k, 0) for k in target}
    over_target = [k for k, v in drift.items() if target.get(k, 0) > 0 and counts.get(k, 0) > target[k]]
    status = STATUS_REVIEW if over_target else STATUS_PASS
    return _result(rule, status, current_counts=counts, target_ratio=target, over_target=over_target)


def check_bpm_repetition(song: dict, rule: dict) -> dict:
    catalog = song.get("catalog_context") or {}
    recent_bpms = catalog.get(rule["catalog_field"])
    bpm = song.get("bpm")
    if recent_bpms is None or bpm is None:
        return _result(rule, STATUS_INSUFFICIENT_EVIDENCE, reason="recent_bpms 또는 bpm 데이터 없음")

    close = [b for b in recent_bpms if abs(b - bpm) <= 2]
    status = STATUS_REVIEW if len(close) >= rule["cluster_threshold"] else STATUS_PASS
    return _result(rule, status, bpm=bpm, close_matches_in_catalog=close)


def check_no_fabricated_identifiers(song: dict, rule: dict) -> dict:
    release = song.get(rule["release_field"])
    if not release or release.get("mode") != "RELEASE":
        return _result(rule, STATUS_NOT_APPLICABLE, reason="RELEASE 모드 아님")

    confirmed = bool(release.get(rule["confirmed_flag_field"]))
    suspicious = []
    for field in rule["identifier_fields"]:
        value = release.get(field)
        if value and value != "PENDING" and not confirmed:
            suspicious.append({"field": field, "value": value})

    status = STATUS_FAIL if suspicious else STATUS_PASS
    return _result(rule, status, suspicious_identifiers=suspicious)


def check_release_field_presence(song: dict, rule: dict) -> dict:
    release = song.get(rule["release_field"])
    if not release or release.get("mode") != "RELEASE":
        return _result(rule, STATUS_NOT_APPLICABLE, reason="RELEASE 모드 아님")

    missing = [f for f in rule["required_subfields"] if not release.get(f)]
    status = STATUS_REVIEW if missing else STATUS_PASS
    return _result(rule, status, missing_fields=missing)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

_CHECKERS = {
    "char_limit": lambda song, rule, cfg: check_char_limit(song, rule),
    "char_recommended_range": lambda song, rule, cfg: check_char_recommended_range(song, rule),
    "structure_required": lambda song, rule, cfg: check_structure_required(song, rule, cfg["structure"]),
    "structure_order": lambda song, rule, cfg: check_structure_order(song, rule, cfg["structure"]),
    "range_with_justification": lambda song, rule, cfg: check_bpm_range_with_justification(song, rule),
    "word_range_by_mood": lambda song, rule, cfg: check_word_range_by_mood(song, rule),
    "avoid_terms": lambda song, rule, cfg: check_avoid_terms(song, rule),
    "forbidden_reference": lambda song, rule, cfg: check_forbidden_reference(song, rule),
    "soft_field_presence": lambda song, rule, cfg: check_soft_field_presence(song, rule),
    "cliche_scan": lambda song, rule, cfg: check_cliche_scan(song, rule),
    "requires_audio": lambda song, rule, cfg: check_requires_audio(song, rule),
    "recent5_overlap": lambda song, rule, cfg: check_recent5_overlap(song, rule),
    "vocal_portfolio": lambda song, rule, cfg: check_vocal_portfolio(song, rule),
    "bpm_repetition": lambda song, rule, cfg: check_bpm_repetition(song, rule),
    "no_fabricated_identifiers": lambda song, rule, cfg: check_no_fabricated_identifiers(song, rule),
    "release_field_presence": lambda song, rule, cfg: check_release_field_presence(song, rule),
}


def _run_category(song: dict, rules_cfg: dict, category: str) -> list[dict]:
    results = []
    for rule in rules_cfg["rules"].get(category, []):
        checker = _CHECKERS.get(rule["type"])
        if checker is None:
            raise ValueError(f"Unknown rule type: {rule['type']} (rule {rule['id']})")
        results.append(checker(song, rule, rules_cfg))
    return results


# Statuses that a category is *never* allowed to emit — this is the
# machine-enforced guarantee that SOFT never auto-PASSes and ADVISORY
# never HARD-FAILs.
_FORBIDDEN_STATUS_BY_CATEGORY = {
    "SOFT": {STATUS_PASS, STATUS_FAIL},
    "ADVISORY": {STATUS_FAIL},
}


# "수리 필요" 등급 — HARD FAIL은 아니지만 MASTER READY를 막는, REVIEW보다
# 심각한 결함. SOFT는 REPAIR, CATALOG는 REDESIGN(§19 4+ 겹침), RELEASE는
# FAIL(예: 가짜 식별자)이 여기 해당한다.
_REPAIR_TIER_STATUSES = {
    "SOFT": {STATUS_REPAIR},
    "CATALOG": {STATUS_REDESIGN},
    "RELEASE": {STATUS_FAIL},
}

# "검수 필요" 등급 — 아직 해결되지 않은 REVIEW. REPAIR 등급보다는 가볍지만
# 그 자체로 MASTER READY를 막는다 (근거 없이 승격하지 않는다).
_REVIEW_TIER_STATUSES = {
    "ADVISORY": {STATUS_REVIEW},
    "CATALOG": {STATUS_REVIEW},
    "RELEASE": {STATUS_REVIEW},
}


def evaluate(song: dict, rules_cfg: dict | None = None) -> dict:
    """song(dict)을 판정하고 SAMDADORA JUDGE REPORT용 dict를 반환한다.

    verdict는 다음 네 가지 중 하나이며, 이 순서로 우선순위를 갖는다:
      1. MASTER FAIL — HARD BLOCK : HARD 규칙 위반이 하나라도 있음
      2. NEEDS REPAIR             : SOFT REPAIR / CATALOG REDESIGN /
                                    RELEASE FAIL 중 하나라도 있음
      3. NEEDS REVIEW             : ADVISORY / CATALOG / RELEASE REVIEW 중
                                    하나라도 해결되지 않고 남아 있음
      4. MASTER READY             : 위 세 가지가 전부 없음 (HARD 전부 PASS,
                                    필수 REPAIR/REDESIGN 없음, 미해결 REVIEW
                                    없음)

    master_pass(bool)는 정확히 verdict == MASTER READY와 동치이다 — "HARD만
    통과하면 PASS"라는 예전 의미로 되돌아가지 않도록, 이 필드 하나만 보고도
    실제로 출고 가능한 상태인지 착오 없이 판단할 수 있게 한다.
    """
    if rules_cfg is None:
        rules_cfg = load_rules()

    report: dict[str, list[dict]] = {}
    for category in ("HARD", "ADVISORY", "SOFT", "CATALOG", "RELEASE"):
        results = _run_category(song, rules_cfg, category)
        forbidden = _FORBIDDEN_STATUS_BY_CATEGORY.get(category)
        if forbidden:
            for r in results:
                if r["status"] in forbidden:
                    raise AssertionError(
                        f"규칙 엔진 내부 오류: {category} 카테고리 규칙 {r['id']}가 "
                        f"허용되지 않는 status {r['status']}를 반환했다."
                    )
        report[category] = results

    hard_failed = [r for r in report["HARD"] if r["status"] == STATUS_FAIL]

    needs_repair = [
        r for category, statuses in _REPAIR_TIER_STATUSES.items()
        for r in report[category] if r["status"] in statuses
    ]
    needs_review = [
        r for category, statuses in _REVIEW_TIER_STATUSES.items()
        for r in report[category] if r["status"] in statuses
    ]

    if hard_failed:
        verdict = VERDICT_HARD_BLOCK
    elif needs_repair:
        verdict = VERDICT_NEEDS_REPAIR
    elif needs_review:
        verdict = VERDICT_NEEDS_REVIEW
    else:
        verdict = VERDICT_MASTER_READY

    master_pass = verdict == VERDICT_MASTER_READY

    return {
        "master_pass": master_pass,
        "verdict": verdict,
        "hard_failed_ids": [r["id"] for r in hard_failed],
        "needs_repair_ids": [r["id"] for r in needs_repair],
        "needs_review_ids": [r["id"] for r in needs_review],
        "categories": report,
    }
