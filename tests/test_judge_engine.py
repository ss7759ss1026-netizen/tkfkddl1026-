"""
SAMDADORA JUDGE ENGINE 테스트.

과제 요구사항에 따라 다음을 반드시 검증한다:
  - prompt 999자 PASS / 1000자 PASS / 1001자 HARD FAIL
  - prompt 850~950자 권장 범위(ADVISORY)
  - lyric sung-word 경계값 (일반 160~200, Café/Work 예외 120~150)
  - BPM 경계값 (95~120, ADVISORY, 근거 제공 시 예외)
  - 필수 구조 요소 누락 시 HARD FAIL
  - 금지 요소 / 아티스트 레퍼런스 탐지
  - HARD FAIL이 하나라도 있으면 MASTER PASS가 절대 나오지 않는 것
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
        "bpm": 100,
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

def test_valid_song_is_master_pass():
    report = evaluate(base_song())
    assert report["master_pass"] is True
    assert report["verdict"] == "MASTER PASS"
    assert report["hard_failed_ids"] == []


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
    assert report["master_pass"] is True


def test_prompt_1000_chars_pass():
    song = base_song()
    song["suno_style_prompt"] = "x" * 1000
    report = evaluate(song)
    result = get_result(report, "HARD", "H1_PROMPT_CHAR_LIMIT")
    assert result["status"] == je.STATUS_PASS
    assert result["value"] == 1000
    assert report["master_pass"] is True


def test_prompt_1001_chars_hard_fail():
    song = base_song()
    song["suno_style_prompt"] = "x" * 1001
    report = evaluate(song)
    result = get_result(report, "HARD", "H1_PROMPT_CHAR_LIMIT")
    assert result["status"] == je.STATUS_FAIL
    assert result["value"] == 1001
    assert report["master_pass"] is False
    assert "H1_PROMPT_CHAR_LIMIT" in report["hard_failed_ids"]
    assert report["verdict"] == "MASTER FAIL — HARD BLOCK"


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
    # ADVISORY는 절대 FAIL이 아니고, MASTER PASS를 막지 않는다.
    assert report["master_pass"] is True


def test_prompt_951_chars_above_recommended_but_under_hard_limit():
    song = base_song()
    song["suno_style_prompt"] = "x" * 951
    report = evaluate(song)
    advisory = get_result(report, "ADVISORY", "A2_PROMPT_RECOMMENDED_RANGE")
    hard = get_result(report, "HARD", "H1_PROMPT_CHAR_LIMIT")
    assert advisory["status"] == je.STATUS_REVIEW
    assert hard["status"] == je.STATUS_PASS
    assert report["master_pass"] is True


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
# BPM boundary — ADVISORY, default 95–120, justification exception
# ---------------------------------------------------------------------------

def test_bpm_95_lower_boundary_pass():
    song = base_song()
    song["bpm"] = 95
    result = get_result(evaluate(song), "ADVISORY", "A1_BPM_DEFAULT_RANGE")
    assert result["status"] == je.STATUS_PASS


def test_bpm_120_upper_boundary_pass():
    song = base_song()
    song["bpm"] = 120
    result = get_result(evaluate(song), "ADVISORY", "A1_BPM_DEFAULT_RANGE")
    assert result["status"] == je.STATUS_PASS


def test_bpm_94_without_justification_is_review():
    song = base_song()
    song["bpm"] = 94
    report = evaluate(song)
    result = get_result(report, "ADVISORY", "A1_BPM_DEFAULT_RANGE")
    assert result["status"] == je.STATUS_REVIEW
    assert report["master_pass"] is True  # ADVISORY는 MASTER PASS를 막지 않는다


def test_bpm_121_without_justification_is_review():
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
        assert report["verdict"] == "MASTER FAIL — HARD BLOCK"
        assert len(report["hard_failed_ids"]) >= 1


def test_multiple_hard_fails_all_reported_and_still_blocked():
    song = base_song()
    song["suno_style_prompt"] = "x" * 1001 + " in the style of Adele"
    song["structure"] = [x for x in VALID_STRUCTURE if x != "Outro"]

    report = evaluate(song)
    assert report["master_pass"] is False
    assert set(report["hard_failed_ids"]) == {
        "H1_PROMPT_CHAR_LIMIT", "H2_STRUCTURE_REQUIRED", "H3_ARTIST_REFERENCE_FORBIDDEN",
    }


def test_advisory_and_soft_issues_never_block_master_pass_alone():
    song = base_song()
    song["bpm"] = 200  # ADVISORY REVIEW, no justification
    song["lyrics"] = make_words(10)  # ADVISORY REVIEW (too short)
    song["human_truth"] = ""  # SOFT REPAIR
    del song["signature"]  # SOFT REPAIR

    report = evaluate(song)
    assert report["master_pass"] is True
    assert report["verdict"] == "MASTER PASS — REVIEW NEEDED"


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
