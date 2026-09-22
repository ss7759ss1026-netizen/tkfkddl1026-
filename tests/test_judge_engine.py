"""
SAMDADORA JUDGE ENGINE 테스트.

과제 요구사항에 따라 다음을 반드시 검증한다:
  - prompt 999자 PASS / 1000자 PASS / 1001자 HARD BLOCK
  - prompt 850~950자 권장 범위(ADVISORY)
  - lyric sung-word 경계값 (일반 160~200, Café/Work 예외 120~150)
  - BPM 경계값 (102~120, ADVISORY, 근거 제공 시 예외 — 2026-09-21 SAMDADORA 결정으로
    기본 탐색 범위 하한이 95에서 102로 갱신됨)
  - 필수 구조 요소 누락 시 HARD BLOCK
  - 금지 요소 / 아티스트 레퍼런스 탐지
  - HARD FAIL이 하나라도 있으면 MASTER READY가 절대 나오지 않는 것

verdict 상태 모델 (2026-09-22 수정 — MASTER PASS 의미 충돌 해소):
  MASTER FAIL — HARD BLOCK : HARD 규칙 위반 존재
  NEEDS REPAIR             : HARD는 전부 PASS했지만 SOFT REPAIR /
                             CATALOG REDESIGN / RELEASE FAIL 중 하나라도 존재
  NEEDS REVIEW             : 위 REPAIR 등급은 없지만 ADVISORY/CATALOG/
                             RELEASE REVIEW가 미해결로 남아 있음
  MASTER READY             : 위 세 가지가 전부 없음 (실제로 출고 가능)
master_pass(bool)는 정확히 verdict == "MASTER READY"와 동치이다. ADVISORY
REVIEW나 SOFT REPAIR가 남아 있는데 "PASS"라고 표시되는 일은 없어야 한다.
"""

import copy

import judge_engine as je

VALID_STRUCTURE = [
    "Intro", "Verse 1", "Pre-chorus", "Chorus", "Tag",
    "Verse 2", "Pre-chorus", "Chorus", "Instrumental Break",
    "Final Chorus", "Final Tag", "Outro",
]


def make_words(n: int) -> str:
    return " ".join(["la"] * n)


def base_song() -> dict:
    return {
        "title": "Coastal Afternoon",
        "suno_style_prompt": "x" * 900,
        "lyrics": make_words(180),
        "structure": list(VALID_STRUCTURE),
        "bpm": 108,
        "mood_palette": "general",
        "human_truth": "A quiet promise to keep moving forward, one small day at a time.",
        "signature": "3-note guitar harmonic motif before every chorus",
    }


def evaluate(song: dict) -> dict:
    return je.evaluate(song, je.load_rules())


def get_result(report: dict, category: str, rule_id: str) -> dict:
    for r in report["categories"][category]:
        if r["id"] == rule_id:
            return r
    raise AssertionError(f"rule {rule_id} not found in category {category}")


# ---------------------------------------------------------------------------
# Sanity: a fully valid song passes everything
# ---------------------------------------------------------------------------

def test_valid_song_is_master_ready():
    # 모든 필수 게이트(HARD 전부 PASS, REPAIR/REDESIGN 없음, 미해결 REVIEW
    # 없음)가 충족되면 MASTER READY여야 한다.
    report = evaluate(base_song())
    assert report["verdict"] == je.VERDICT_MASTER_READY
    assert report["master_pass"] is True
    assert report["hard_failed_ids"] == []
    assert report["needs_repair_ids"] == []
    assert report["needs_review_ids"] == []


# ---------------------------------------------------------------------------
# Prompt character limit — HARD (CLAUDE.md PART B §45)
# ---------------------------------------------------------------------------

def test_prompt_999_chars_pass():
    song = base_song()
    song["suno_style_prompt"] = "x" * 999
    report = evaluate(song)
    result = get_result(report, "HARD", "H1_PROMPT_CHAR_LIMIT")
    assert result["status"] == je.STATUS_PASS
    assert result["value"] == 999
    # H1 자체는 통과 — 999자는 850~950 권장 범위 밖이라 NEEDS REVIEW로
    # 남을 뿐, HARD BLOCK은 아니어야 한다.
    assert report["hard_failed_ids"] == []
    assert report["verdict"] != je.VERDICT_HARD_BLOCK


def test_prompt_1000_chars_pass():
    song = base_song()
    song["suno_style_prompt"] = "x" * 1000
    report = evaluate(song)
    result = get_result(report, "HARD", "H1_PROMPT_CHAR_LIMIT")
    assert result["status"] == je.STATUS_PASS
    assert result["value"] == 1000
    assert report["hard_failed_ids"] == []
    assert report["verdict"] != je.VERDICT_HARD_BLOCK


def test_prompt_1001_chars_hard_fail():
    song = base_song()
    song["suno_style_prompt"] = "x" * 1001
    report = evaluate(song)
    result = get_result(report, "HARD", "H1_PROMPT_CHAR_LIMIT")
    assert result["status"] == je.STATUS_FAIL
    assert result["value"] == 1001
    assert report["master_pass"] is False
    assert "H1_PROMPT_CHAR_LIMIT" in report["hard_failed_ids"]
    assert report["verdict"] == je.VERDICT_HARD_BLOCK


def test_prompt_char_count_is_actually_computed_not_estimated():
    # len()이 정말로 호출되는지 — 공백을 포함한 임의 길이로 확인
    song = base_song()
    song["suno_style_prompt"] = "word " * 100  # 500 chars exactly
    result = get_result(evaluate(song), "HARD", "H1_PROMPT_CHAR_LIMIT")
    assert result["value"] == len("word " * 100) == 500


# ---------------------------------------------------------------------------
# Prompt recommended range 850–950 — ADVISORY (never FAIL, never blocks pass)
# ---------------------------------------------------------------------------

def test_prompt_850_chars_within_recommended():
    song = base_song()
    song["suno_style_prompt"] = "x" * 850
    result = get_result(evaluate(song), "ADVISORY", "A2_PROMPT_RECOMMENDED_RANGE")
    assert result["status"] == je.STATUS_PASS


def test_prompt_950_chars_within_recommended():
    song = base_song()
    song["suno_style_prompt"] = "x" * 950
    result = get_result(evaluate(song), "ADVISORY", "A2_PROMPT_RECOMMENDED_RANGE")
    assert result["status"] == je.STATUS_PASS


def test_prompt_849_chars_below_recommended_is_review_not_fail():
    song = base_song()
    song["suno_style_prompt"] = "x" * 849
    report = evaluate(song)
    result = get_result(report, "ADVISORY", "A2_PROMPT_RECOMMENDED_RANGE")
    assert result["status"] == je.STATUS_REVIEW
    # ADVISORY는 절대 FAIL이 아니므로 HARD BLOCK은 아니지만, 미해결
    # REVIEW이므로 MASTER READY도 아니다 — NEEDS REVIEW로 남아야 한다.
    assert report["hard_failed_ids"] == []
    assert report["master_pass"] is False
    assert report["verdict"] == je.VERDICT_NEEDS_REVIEW
    assert "A2_PROMPT_RECOMMENDED_RANGE" in report["needs_review_ids"]


def test_prompt_951_chars_above_recommended_but_under_hard_limit():
    song = base_song()
    song["suno_style_prompt"] = "x" * 951
    report = evaluate(song)
    advisory = get_result(report, "ADVISORY", "A2_PROMPT_RECOMMENDED_RANGE")
    hard = get_result(report, "HARD", "H1_PROMPT_CHAR_LIMIT")
    assert advisory["status"] == je.STATUS_REVIEW
    assert hard["status"] == je.STATUS_PASS
    # 1,000자 HARD LIMIT은 통과했지만 권장 범위 밖이라 여전히 REVIEW 대상.
    assert report["master_pass"] is False
    assert report["verdict"] == je.VERDICT_NEEDS_REVIEW


# ---------------------------------------------------------------------------
# Sung word boundary — ADVISORY, general 160–200 / Café-Work 120–150
# ---------------------------------------------------------------------------

def test_sung_words_general_lower_boundary_160_pass():
    song = base_song()
    song["lyrics"] = make_words(160)
    result = get_result(evaluate(song), "ADVISORY", "A3_SUNG_WORDS")
    assert result["status"] == je.STATUS_PASS
    assert result["value"] == 160


def test_sung_words_general_upper_boundary_200_pass():
    song = base_song()
    song["lyrics"] = make_words(200)
    result = get_result(evaluate(song), "ADVISORY", "A3_SUNG_WORDS")
    assert result["status"] == je.STATUS_PASS
    assert result["value"] == 200


def test_sung_words_general_159_is_review():
    song = base_song()
    song["lyrics"] = make_words(159)
    result = get_result(evaluate(song), "ADVISORY", "A3_SUNG_WORDS")
    assert result["status"] == je.STATUS_REVIEW


def test_sung_words_general_201_is_review():
    song = base_song()
    song["lyrics"] = make_words(201)
    result = get_result(evaluate(song), "ADVISORY", "A3_SUNG_WORDS")
    assert result["status"] == je.STATUS_REVIEW


def test_sung_words_section_labels_are_not_counted_as_words():
    song = base_song()
    song["lyrics"] = "[Verse 1] " + make_words(160) + " [Chorus]"
    result = get_result(evaluate(song), "ADVISORY", "A3_SUNG_WORDS")
    assert result["value"] == 160


def test_sung_words_cafe_work_exception_range():
    song = base_song()
    song["mood_palette"] = "cafe_work"

    song["lyrics"] = make_words(120)
    r120 = get_result(evaluate(song), "ADVISORY", "A3_SUNG_WORDS")
    assert r120["status"] == je.STATUS_PASS
    assert r120["mood_exception_applied"] is True

    song["lyrics"] = make_words(150)
    r150 = get_result(evaluate(song), "ADVISORY", "A3_SUNG_WORDS")
    assert r150["status"] == je.STATUS_PASS

    song["lyrics"] = make_words(119)
    r119 = get_result(evaluate(song), "ADVISORY", "A3_SUNG_WORDS")
    assert r119["status"] == je.STATUS_REVIEW

    song["lyrics"] = make_words(151)
    r151 = get_result(evaluate(song), "ADVISORY", "A3_SUNG_WORDS")
    assert r151["status"] == je.STATUS_REVIEW

    # Café/Work 예외를 일반곡에 적용하면 160단어도 REVIEW로 나와야 한다
    # (일반 범위 160~200과 café 범위 120~150은 서로 다른 기준선이므로).
    song["mood_palette"] = "general"
    song["lyrics"] = make_words(150)
    r_general_150 = get_result(evaluate(song), "ADVISORY", "A3_SUNG_WORDS")
    assert r_general_150["status"] == je.STATUS_REVIEW


# ---------------------------------------------------------------------------
# BPM boundary — ADVISORY, default 102–120 (2026-09-21 SAMDADORA 결정으로
# 기존 95–120에서 하한 갱신), justification exception
# ---------------------------------------------------------------------------

def test_bpm_101_below_lower_boundary_is_review():
    song = base_song()
    song["bpm"] = 101
    report = evaluate(song)
    result = get_result(report, "ADVISORY", "A1_BPM_DEFAULT_RANGE")
    assert result["status"] == je.STATUS_REVIEW
    # ADVISORY REVIEW는 HARD BLOCK은 아니지만, 미해결 REVIEW로 남아 있는 한
    # MASTER READY도 아니다.
    assert report["hard_failed_ids"] == []
    assert report["master_pass"] is False
    assert report["verdict"] == je.VERDICT_NEEDS_REVIEW


def test_bpm_102_lower_boundary_pass():
    song = base_song()
    song["bpm"] = 102
    result = get_result(evaluate(song), "ADVISORY", "A1_BPM_DEFAULT_RANGE")
    assert result["status"] == je.STATUS_PASS
    assert result["value"] == 102
    assert result["range"] == [102, 120]


def test_bpm_120_upper_boundary_pass():
    song = base_song()
    song["bpm"] = 120
    result = get_result(evaluate(song), "ADVISORY", "A1_BPM_DEFAULT_RANGE")
    assert result["status"] == je.STATUS_PASS


def test_bpm_121_above_upper_boundary_is_review():
    song = base_song()
    song["bpm"] = 121
    result = get_result(evaluate(song), "ADVISORY", "A1_BPM_DEFAULT_RANGE")
    assert result["status"] == je.STATUS_REVIEW


def test_bpm_out_of_range_with_justification_passes():
    song = base_song()
    song["bpm"] = 132
    song["bpm_justification"] = "Drive/Travel/Coastal 팔레트의 rolling bass 그루브를 위해 의도적으로 상향."
    result = get_result(evaluate(song), "ADVISORY", "A1_BPM_DEFAULT_RANGE")
    assert result["status"] == je.STATUS_PASS
    assert result.get("note") == "JUSTIFIED DEVIATION"


def test_bpm_now_excluded_lower_zone_with_justification_passes():
    # 95~101 BPM은 기존 기준에서는 PASS였으나 새 기준(102~120)에서는 범위 밖이다.
    # 근거가 있으면 여전히 JUSTIFIED DEVIATION으로 PASS 처리되어야 한다.
    song = base_song()
    song["bpm"] = 98
    song["bpm_justification"] = "Café/Work 팔레트의 느린 그루브를 의도적으로 유지하기 위해 하향."
    result = get_result(evaluate(song), "ADVISORY", "A1_BPM_DEFAULT_RANGE")
    assert result["status"] == je.STATUS_PASS
    assert result.get("note") == "JUSTIFIED DEVIATION"


def test_bpm_now_excluded_lower_zone_without_justification_is_review():
    song = base_song()
    song["bpm"] = 98
    result = get_result(evaluate(song), "ADVISORY", "A1_BPM_DEFAULT_RANGE")
    assert result["status"] == je.STATUS_REVIEW
    assert result.get("note") != "JUSTIFIED DEVIATION"


# ---------------------------------------------------------------------------
# Missing required structure — HARD (CLAUDE.md PART B §28/§61)
# ---------------------------------------------------------------------------

def test_missing_required_structure_is_hard_fail():
    song = base_song()
    structure = list(VALID_STRUCTURE)
    structure.remove("Outro")
    song["structure"] = structure

    report = evaluate(song)
    result = get_result(report, "HARD", "H2_STRUCTURE_REQUIRED")
    assert result["status"] == je.STATUS_FAIL
    assert any(m["section"] == "Outro" for m in result["missing_required_sections"])
    assert report["master_pass"] is False
    assert "H2_STRUCTURE_REQUIRED" in report["hard_failed_ids"]


def test_missing_second_prechorus_or_chorus_is_hard_fail():
    song = base_song()
    # Pre-chorus/Chorus가 정확히 한 번만 있으면(2절 반복 누락) 필수 개수 미달.
    song["structure"] = ["Intro", "Verse 1", "Pre-chorus", "Chorus", "Tag",
                          "Verse 2", "Instrumental Break", "Final Chorus",
                          "Final Tag", "Outro"]
    result = get_result(evaluate(song), "HARD", "H2_STRUCTURE_REQUIRED")
    assert result["status"] == je.STATUS_FAIL


def test_bridge_missing_is_not_a_failure():
    # Bridge는 선택 요소이므로 없어도 통과해야 한다 (VALID_STRUCTURE에는 원래 없음).
    result = get_result(evaluate(base_song()), "HARD", "H2_STRUCTURE_REQUIRED")
    assert result["status"] == je.STATUS_PASS


def test_structure_can_be_parsed_from_lyrics_labels_when_not_given_explicitly():
    song = base_song()
    del song["structure"]
    song["lyrics"] = " ".join(f"[{s}] " + make_words(4) for s in VALID_STRUCTURE)
    result = get_result(evaluate(song), "HARD", "H2_STRUCTURE_REQUIRED")
    assert result["status"] == je.STATUS_PASS


# ---------------------------------------------------------------------------
# Forbidden elements / artist reference detection — HARD (CLAUDE.md §A6)
# ---------------------------------------------------------------------------

def test_artist_name_in_prompt_is_hard_fail():
    song = base_song()
    song["suno_style_prompt"] = "warm coastal indie pop in the vein of Taylor Swift, groove pop"
    report = evaluate(song)
    result = get_result(report, "HARD", "H3_ARTIST_REFERENCE_FORBIDDEN")
    assert result["status"] == je.STATUS_FAIL
    assert "taylor swift" in result["matched_artist_names"]
    assert report["master_pass"] is False


def test_artist_name_in_lyrics_is_hard_fail():
    song = base_song()
    song["lyrics"] = make_words(160) + " BTS forever"
    result = get_result(evaluate(song), "HARD", "H3_ARTIST_REFERENCE_FORBIDDEN")
    assert result["status"] == je.STATUS_FAIL
    assert "bts" in result["matched_artist_names"]


def test_style_mimicry_phrase_is_hard_fail():
    song = base_song()
    song["suno_style_prompt"] = "make it sound exactly like the reference track, warm coastal pop"
    result = get_result(evaluate(song), "HARD", "H3_ARTIST_REFERENCE_FORBIDDEN")
    assert result["status"] == je.STATUS_FAIL
    assert result["matched_reference_patterns"]


def test_clean_prompt_has_no_forbidden_reference():
    result = get_result(evaluate(base_song()), "HARD", "H3_ARTIST_REFERENCE_FORBIDDEN")
    assert result["status"] == je.STATUS_PASS
    assert result["matched_artist_names"] == []
    assert result["matched_reference_patterns"] == []


# ---------------------------------------------------------------------------
# HARD FAIL always blocks MASTER PASS — even combined with other categories
# ---------------------------------------------------------------------------

def test_any_single_hard_fail_blocks_master_pass():
    for mutate in (
        lambda s: s.__setitem__("suno_style_prompt", "x" * 1001),
        lambda s: s.__setitem__("structure", [x for x in VALID_STRUCTURE if x != "Intro"]),
        lambda s: s.__setitem__("lyrics", make_words(160) + " Ed Sheeran"),
    ):
        song = base_song()
        mutate(song)
        report = evaluate(song)
        assert report["master_pass"] is False, report
        assert report["verdict"] == je.VERDICT_HARD_BLOCK
        assert len(report["hard_failed_ids"]) >= 1


def test_multiple_hard_fails_all_reported_and_still_blocked():
    song = base_song()
    song["suno_style_prompt"] = "x" * 1001 + " in the style of Adele"
    song["structure"] = [x for x in VALID_STRUCTURE if x != "Outro"]

    report = evaluate(song)
    assert report["master_pass"] is False
    assert report["verdict"] == je.VERDICT_HARD_BLOCK
    assert set(report["hard_failed_ids"]) == {
        "H1_PROMPT_CHAR_LIMIT", "H2_STRUCTURE_REQUIRED", "H3_ARTIST_REFERENCE_FORBIDDEN",
    }


# ---------------------------------------------------------------------------
# MASTER PASS 의미 충돌 수정 (2026-09-22 리뷰) — HARD는 전부 PASS해도
# SOFT REPAIR / CATALOG REDESIGN / 미해결 REVIEW가 있으면 절대 "PASS"라고
# 표시하지 않는다. NEEDS REPAIR / NEEDS REVIEW로 명확히 구분한다.
# ---------------------------------------------------------------------------

def test_unresolved_advisory_review_alone_prevents_master_ready():
    # HARD 전부 PASS, SOFT도 REPAIR 없음(필드 존재) — 오직 ADVISORY REVIEW만
    # 남아 있는 경우. HARD BLOCK은 아니지만 MASTER READY도 아니어야 한다.
    song = base_song()
    song["bpm"] = 200  # ADVISORY REVIEW, 근거 없음

    report = evaluate(song)
    assert report["hard_failed_ids"] == []
    assert report["needs_repair_ids"] == []
    assert report["master_pass"] is False
    assert report["verdict"] == je.VERDICT_NEEDS_REVIEW
    assert "A1_BPM_DEFAULT_RANGE" in report["needs_review_ids"]


def test_missing_human_truth_yields_needs_repair():
    song = base_song()
    song["human_truth"] = ""  # SOFT REPAIR

    report = evaluate(song)
    assert report["hard_failed_ids"] == []
    assert report["master_pass"] is False
    assert report["verdict"] == je.VERDICT_NEEDS_REPAIR
    assert "S1_HUMAN_TRUTH_PRESENT" in report["needs_repair_ids"]


def test_missing_signature_yields_needs_repair():
    song = base_song()
    del song["signature"]  # SOFT REPAIR

    report = evaluate(song)
    assert report["hard_failed_ids"] == []
    assert report["master_pass"] is False
    assert report["verdict"] == je.VERDICT_NEEDS_REPAIR
    assert "S2_SIGNATURE_MEMORY_PRESENT" in report["needs_repair_ids"]


def test_soft_repair_outranks_coexisting_advisory_review():
    # SOFT REPAIR(수리 필요)와 ADVISORY REVIEW(검수 필요)가 동시에 있으면
    # 더 심각한 REPAIR 등급이 verdict를 결정해야 한다 — "PASS"로도,
    # 가벼운 "NEEDS REVIEW"로도 축소 표시하지 않는다.
    song = base_song()
    song["bpm"] = 200  # ADVISORY REVIEW
    song["lyrics"] = make_words(10)  # ADVISORY REVIEW (too short)
    song["human_truth"] = ""  # SOFT REPAIR
    del song["signature"]  # SOFT REPAIR

    report = evaluate(song)
    assert report["hard_failed_ids"] == []
    assert report["master_pass"] is False
    assert report["verdict"] == je.VERDICT_NEEDS_REPAIR
    assert set(report["needs_repair_ids"]) == {"S1_HUMAN_TRUTH_PRESENT", "S2_SIGNATURE_MEMORY_PRESENT"}
    assert "A1_BPM_DEFAULT_RANGE" in report["needs_review_ids"]
    assert "A3_SUNG_WORDS" in report["needs_review_ids"]


def test_catalog_redesign_prevents_master_ready():
    song = base_song()
    song["catalog_context"] = {"recent5_overlap_count": 4}  # §19 4+ → REDESIGN

    report = evaluate(song)
    catalog_result = get_result(report, "CATALOG", "C1_RECENT5_DIFFERENTIATION")
    assert catalog_result["status"] == je.STATUS_REDESIGN
    assert report["hard_failed_ids"] == []
    assert report["master_pass"] is False
    assert report["verdict"] == je.VERDICT_NEEDS_REPAIR
    assert "C1_RECENT5_DIFFERENTIATION" in report["needs_repair_ids"]


def test_catalog_review_alone_yields_needs_review_not_repair():
    song = base_song()
    song["catalog_context"] = {"recent5_overlap_count": 3}  # §19 3 → REVIEW

    report = evaluate(song)
    assert report["needs_repair_ids"] == []
    assert report["master_pass"] is False
    assert report["verdict"] == je.VERDICT_NEEDS_REVIEW
    assert "C1_RECENT5_DIFFERENTIATION" in report["needs_review_ids"]


def test_release_fabricated_identifier_prevents_master_ready():
    song = base_song()
    song["release"] = {
        "mode": "RELEASE",
        "isrc": "USRC12345678",
        "identifiers_confirmed": False,
    }

    report = evaluate(song)
    assert report["hard_failed_ids"] == []
    assert report["master_pass"] is False
    assert report["verdict"] == je.VERDICT_NEEDS_REPAIR
    assert "R1_NO_FABRICATED_IDENTIFIERS" in report["needs_repair_ids"]


def test_unassessed_and_insufficient_evidence_do_not_block_master_ready():
    # SOFT UNASSESSED(감사 대기)와 CATALOG INSUFFICIENT EVIDENCE/RELEASE NOT
    # APPLICABLE은 "근거 없이 READY로 승격"되지는 않지만(각 rule 결과는
    # 여전히 UNASSESSED/INSUFFICIENT EVIDENCE로 남는다), 그 자체가 전체
    # verdict를 막지도 않는다 — base_song()이 정확히 이 상태다.
    report = evaluate(base_song())
    soft_statuses = {r["status"] for r in report["categories"]["SOFT"]}
    assert soft_statuses <= {je.STATUS_UNASSESSED, je.STATUS_REPAIR}
    assert je.STATUS_UNASSESSED in soft_statuses
    catalog_statuses = {r["status"] for r in report["categories"]["CATALOG"]}
    assert catalog_statuses == {je.STATUS_INSUFFICIENT_EVIDENCE}
    release_statuses = {r["status"] for r in report["categories"]["RELEASE"]}
    assert release_statuses == {je.STATUS_NOT_APPLICABLE}

    assert report["verdict"] == je.VERDICT_MASTER_READY
    assert report["master_pass"] is True


# ---------------------------------------------------------------------------
# SOFT rules must never silently auto-PASS
# ---------------------------------------------------------------------------

def test_soft_rules_never_return_pass_status():
    report = evaluate(base_song())
    for result in report["categories"]["SOFT"]:
        assert result["status"] in (je.STATUS_UNASSESSED, je.STATUS_REPAIR)
        assert result["status"] != je.STATUS_PASS


def test_soft_empty_human_truth_is_repair_not_pass():
    song = base_song()
    song["human_truth"] = ""
    result = get_result(evaluate(song), "SOFT", "S1_HUMAN_TRUTH_PRESENT")
    assert result["status"] == je.STATUS_REPAIR


def test_soft_present_human_truth_is_unassessed_not_pass():
    result = get_result(evaluate(base_song()), "SOFT", "S1_HUMAN_TRUTH_PRESENT")
    assert result["status"] == je.STATUS_UNASSESSED


def test_soft_audio_gates_require_audio_flag():
    song = base_song()
    result = get_result(evaluate(song), "SOFT", "S4_VOCAL_GATE")
    assert result["status"] == je.STATUS_UNASSESSED
    assert "AUDIO REQUIRED" in result["reason"]


# ---------------------------------------------------------------------------
# CATALOG / RELEASE: missing data must not be guessed into a PASS
# ---------------------------------------------------------------------------

def test_catalog_rules_are_insufficient_evidence_without_catalog_context():
    report = evaluate(base_song())
    for result in report["categories"]["CATALOG"]:
        assert result["status"] == je.STATUS_INSUFFICIENT_EVIDENCE


def test_catalog_recent5_overlap_thresholds():
    song = base_song()
    song["catalog_context"] = {"recent5_overlap_count": 2}
    assert get_result(evaluate(song), "CATALOG", "C1_RECENT5_DIFFERENTIATION")["status"] == je.STATUS_PASS

    song["catalog_context"] = {"recent5_overlap_count": 3}
    assert get_result(evaluate(song), "CATALOG", "C1_RECENT5_DIFFERENTIATION")["status"] == je.STATUS_REVIEW

    song["catalog_context"] = {"recent5_overlap_count": 4}
    assert get_result(evaluate(song), "CATALOG", "C1_RECENT5_DIFFERENTIATION")["status"] == je.STATUS_REDESIGN


def test_release_rules_not_applicable_without_release_mode():
    report = evaluate(base_song())
    for result in report["categories"]["RELEASE"]:
        assert result["status"] == je.STATUS_NOT_APPLICABLE


def test_release_fabricated_identifier_is_fail():
    song = base_song()
    song["release"] = {
        "mode": "RELEASE",
        "isrc": "USRC12345678",
        "identifiers_confirmed": False,
    }
    result = get_result(evaluate(song), "RELEASE", "R1_NO_FABRICATED_IDENTIFIERS")
    assert result["status"] == je.STATUS_FAIL


def test_release_pending_identifier_is_pass():
    song = base_song()
    song["release"] = {"mode": "RELEASE", "isrc": "PENDING"}
    result = get_result(evaluate(song), "RELEASE", "R1_NO_FABRICATED_IDENTIFIERS")
    assert result["status"] == je.STATUS_PASS
