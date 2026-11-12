"""Summarise a `claude plugin eval` run as the Markdown table used in docs/evals.md.

Usage: python3 -I scripts/summarize_results.py RUN.json [--check]

RUN.json is the file written by `claude plugin eval --json RUN.json`, or the
`aggregate-result.json` in a results directory. Standard library only.

Graders are split in two groups (see `fmt()` in evals/generate.py):

  - behaviour checks are scored in both arms; the delta is computed from them.
  - format checks (`arm: with-only`) test the skill's own output format. They
    are reported as passed/total for the skill arm and never enter the delta.

--check exits 1 when a behaviour check or a format check fails in the skill
arm, so a format regression still fails a run even though it is not scored.
"""
import argparse
import json
import sys
from pathlib import Path


def is_format(grader):
    return (grader.get("config") or {}).get("arm") == "with-only"


def behaviour_score(run, format_names):
    """Weighted share of behaviour graders that passed in one run."""
    graders = [g for g in run["graders"] if g["name"] not in format_names]
    total = sum(g["weight"] for g in graders)
    return sum(g["weight"] for g in graders if g["passed"]) / total if total else None


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def summarise(case):
    format_names = {g["name"] for g in case["graders"] if is_format(g)}
    with_runs = case["arms"].get("with") or []
    without_runs = case["arms"].get("without") or []
    with_scores = [behaviour_score(r, format_names) for r in with_runs]
    fmt_results = [g["passed"] for r in with_runs for g in r["graders"] if g["name"] in format_names]
    score = mean(with_scores)
    baseline = mean(behaviour_score(r, format_names) for r in without_runs)
    return {
        "name": case["name"],
        "runs": len(with_runs),
        "score": score,
        "runs_passed": sum(1 for s in with_scores if s == 1),
        "baseline": baseline,
        "delta": None if score is None or baseline is None else score - baseline,
        "format_passed": sum(1 for p in fmt_results if p),
        "format_total": len(fmt_results),
        "errors": [r["error"] for r in with_runs + without_runs if r.get("error")],
    }


def num(value, signed=False):
    if value is None:
        return "n/a"
    return f"{value:+.2f}" if signed else f"{value:.2f}"


def table(rows):
    lines = ["| Case | Behaviour, with skill | Runs passed | Behaviour, without skill | Delta | Format checks |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        fmt = f"{r['format_passed']}/{r['format_total']}" if r["format_total"] else "none"
        lines.append(f"| {r['name']} | {num(r['score'])} | {r['runs_passed']}/{r['runs']} | "
                     f"{num(r['baseline'])} | {num(r['delta'], signed=True)} | {fmt} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Summarise a claude plugin eval run.")
    parser.add_argument("run", type=Path, help="run JSON (--json output or aggregate-result.json)")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if any behaviour or format check failed in the skill arm")
    args = parser.parse_args()

    data = json.loads(args.run.read_text(encoding="utf-8"))
    rows = [summarise(c) for c in data["cases"]]
    deltas = [r["delta"] for r in rows if r["delta"] is not None]
    runs = sum(r["runs"] for r in rows)
    runs_passed = sum(r["runs_passed"] for r in rows)
    fmt_passed = sum(r["format_passed"] for r in rows)
    fmt_total = sum(r["format_total"] for r in rows)

    print(table(rows))
    print()
    print(f"Claude Code {data.get('claudeVersion', '?')}, started {data.get('startedAt', '?')}, "
          f"cost ${data.get('costUsd', 0):.2f}{', PARTIAL RUN' if data.get('partial') else ''}.")
    print(f"Behaviour: {runs_passed} of {runs} skill-arm runs passed every behaviour check; "
          f"mean delta over the {len(deltas)} cases with a baseline: {num(mean(deltas), signed=True)}.")
    print(f"Format: {fmt_passed} of {fmt_total} format checks passed in the skill arm.")

    errors = [f"{r['name']}: {e}" for r in rows for e in r["errors"]]
    for e in errors:
        print(f"run error: {e}", file=sys.stderr)
    if args.check and (errors or data.get("partial") or runs_passed != runs or fmt_passed != fmt_total):
        sys.exit(1)


if __name__ == "__main__":
    main()
