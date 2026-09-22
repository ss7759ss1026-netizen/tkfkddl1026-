"""
SAMDADORA JUDGE REPORT CLI

곡 JSON 파일을 judge_engine.evaluate()로 채점하고, 사람이 읽기 쉬운
SAMDADORA JUDGE REPORT를 출력한다. --json 옵션을 주면 원시 JSON 리포트를
그대로 출력한다 (다른 도구/워크플로에서 파싱하기 위함).

사용법:
    python scripts/validate_song.py --input catalog/some-song.json
    python scripts/validate_song.py --input catalog/some-song.json --json
    cat song.json | python scripts/validate_song.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge_engine  # noqa: E402


def _load_song(input_path: str | None) -> dict:
    if input_path:
        with open(input_path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def _fmt_result_line(result: dict) -> str:
    extras = {
        k: v
        for k, v in result.items()
        if k not in ("id", "status", "source", "description") and v not in (None, [], {})
    }
    extra_str = f" | {extras}" if extras else ""
    return f"  [{result['status']:>10}] {result['id']}{extra_str}"


def render_report(report: dict) -> str:
    lines = []
    lines.append("=" * 72)
    lines.append("SAMDADORA JUDGE REPORT")
    lines.append("=" * 72)
    lines.append(f"MASTER VERDICT : {report['verdict']}")
    lines.append(f"READINESS STAGE: {report.get('readiness_stage') or 'N/A (see verdict)'}")
    lines.append(f"MASTER READY   : {report['master_pass']}")
    if report["hard_failed_ids"]:
        lines.append(f"HARD FAIL IDS  : {', '.join(report['hard_failed_ids'])}")
    if report.get("needs_repair_ids"):
        lines.append(f"NEEDS REPAIR   : {', '.join(report['needs_repair_ids'])}")
    if report.get("needs_review_ids"):
        lines.append(f"NEEDS REVIEW   : {', '.join(report['needs_review_ids'])}")
    lines.append("")

    for category in ("HARD", "ADVISORY", "SOFT", "CATALOG", "RELEASE"):
        results = report["categories"][category]
        lines.append(f"--- {category} ({len(results)} rules) ---")
        if not results:
            lines.append("  (no rules)")
        for r in results:
            lines.append(_fmt_result_line(r))
        lines.append("")

    lines.append("=" * 72)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SAMDADORA JUDGE ENGINE — song validator")
    parser.add_argument("--input", "-i", help="곡 JSON 파일 경로 (생략 시 stdin)")
    parser.add_argument("--rules", "-r", default=None, help="judge-rules.json 경로 (기본: config/judge-rules.json)")
    parser.add_argument("--json", action="store_true", help="사람이 읽는 리포트 대신 원시 JSON을 출력")
    args = parser.parse_args(argv)

    song = _load_song(args.input)
    rules_cfg = judge_engine.load_rules(args.rules) if args.rules else judge_engine.load_rules()
    report = judge_engine.evaluate(song, rules_cfg)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_report(report))

    return 0 if report["master_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
