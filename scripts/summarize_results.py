"""Summarise a `claude plugin eval` run as the Markdown table used in docs/evals.md.

Usage: python3 -I scripts/summarize_results.py RUN.json [--check]
           [--save SUMMARY.json [--update]] [--model MODEL]
       python3 -I scripts/summarize_results.py A.json B.json ... [--check]

RUN.json is the file written by `claude plugin eval --json RUN.json`, the
`aggregate-result.json` in a results directory, or a summary written earlier
with --save. Standard library only.

Graders are split in two groups (see `fmt()` in evals/generate.py):

  - behaviour checks are scored in both arms; the delta is computed from them.
  - format checks (`arm: with-only`) test the skill's own output format. They
    are reported as passed/total for the skill arm and never enter the delta.

--check exits 1 when a behaviour check or a format check fails in the skill
arm, so a format regression still fails a run even though it is not scored.

With several files (one run per model) the script prints one comparison table:
behaviour score with and without the skill for each model, side by side.

--save writes a compact summary (scores and per-grader pass counts, no
transcripts and no local paths) that is small enough to commit under
docs/results/. The model id is read from a run transcript when one still
exists (see scripts/collect_traces.py); pass --model when it does not.

--update (with --save) keeps the existing summary and replaces only the cases
that RUN.json holds. Use it after re-running a few cases on their own, for
example after changing a case or the skill. Each case records when it was run;
the table marks cases that were run later than the rest with `*`.
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


def passes(runs, name):
    """How many of these runs passed the named grader; None when it did not run."""
    results = [g["passed"] for r in runs for g in r["graders"] if g["name"] == name]
    return sum(1 for p in results if p) if results else None


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
        "graders": [{"name": g["name"], "type": g["type"], "weight": g["weight"],
                     "kind": "format" if g["name"] in format_names else "behaviour",
                     "passed_with": passes(with_runs, g["name"]),
                     "passed_without": passes(without_runs, g["name"])}
                    for g in case["graders"]],
    }


def detect_model(data):
    """Model id from the first run transcript that still exists, else None."""
    for case in data["cases"]:
        for runs in case["arms"].values():
            for run in runs or []:
                path = Path(run.get("tracePath") or "")
                if not path.is_file():
                    continue
                for line in path.read_text(encoding="utf-8").splitlines():
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    if event.get("type") == "system" and event.get("model"):
                        return event["model"]
    return None


def load(path, model):
    """Return a summary dict from a raw run file or from a saved summary."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if "summary_version" in data:
        return data
    plugins = (data.get("suite") or {}).get("plugins") or [{}]
    return {
        "summary_version": 1,
        "skill_version": plugins[0].get("version"),
        "claude_version": data.get("claudeVersion"),
        "model": model or detect_model(data),
        "started_at": data.get("startedAt"),
        "cost_usd": round(data.get("costUsd") or 0, 2),
        "partial": bool(data.get("partial")),
        "cases": [{**summarise(c), "started_at": data.get("startedAt")} for c in data["cases"]],
    }


def merge(old, new):
    """Replace the cases of an existing summary with the re-run cases in `new`."""
    if old["model"] != new["model"]:
        sys.exit(f"error: --update mixes models: {old['model']} and {new['model']}")
    rerun = {r["name"]: r for r in new["cases"]}
    cases = [rerun.pop(r["name"], r) for r in old["cases"]] + list(rerun.values())
    # cost_usd stays the cost of the full run: partial re-runs are merged in any
    # number of times, so adding their cost would count some of them twice.
    return {**old, "partial": old["partial"] or new["partial"],
            "cases": sorted(cases, key=lambda r: r["name"])}


def rerun_mark(data, row):
    return " *" if row.get("started_at") not in (None, data["started_at"]) else ""


def num(value, signed=False):
    if value is None:
        return "n/a"
    return f"{value:+.2f}" if signed else f"{value:.2f}"


def table(data):
    rows = data["cases"]
    lines = ["| Case | Behaviour, with skill | Runs passed | Behaviour, without skill | Delta | Format checks |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        fmt = f"{r['format_passed']}/{r['format_total']}" if r["format_total"] else "none"
        lines.append(f"| {r['name']}{rerun_mark(data, r)} | {num(r['score'])} | {r['runs_passed']}/{r['runs']} | "
                     f"{num(r['baseline'])} | {num(r['delta'], signed=True)} | {fmt} |")
    return "\n".join(lines)


def totals(data):
    rows = data["cases"]
    deltas = [r["delta"] for r in rows if r["delta"] is not None]
    return {
        "runs": sum(r["runs"] for r in rows),
        "runs_passed": sum(r["runs_passed"] for r in rows),
        "format_passed": sum(r["format_passed"] for r in rows),
        "format_total": sum(r["format_total"] for r in rows),
        "deltas": len(deltas),
        "mean_delta": mean(deltas),
        "errors": [f"{r['name']}: {e}" for r in rows for e in r["errors"]],
    }


def describe(data, t):
    print(f"Skill {data['skill_version'] or '?'}, Claude Code {data['claude_version'] or '?'}, "
          f"model {data['model'] or 'unknown'}, started {data['started_at'] or '?'}, "
          f"cost ${data['cost_usd']:.2f}{', PARTIAL RUN' if data['partial'] else ''}.")
    print(f"Behaviour: {t['runs_passed']} of {t['runs']} skill-arm runs passed every behaviour check; "
          f"mean delta over the {t['deltas']} cases with a baseline: {num(t['mean_delta'], signed=True)}.")
    print(f"Format: {t['format_passed']} of {t['format_total']} format checks passed in the skill arm.")


def comparison(summaries):
    """One row per case, two columns per model: behaviour with and without the skill.
    A skill-arm cell gets a mark when a run failed a behaviour check (!) or a format check (f)."""
    models = [d["model"] or "unknown" for d in summaries]
    lines = ["| Case | " + " | ".join(f"{m}, with skill | {m}, without" for m in models) + " |",
             "|---|" + "---|---|" * len(models)]
    names = []
    for d in summaries:
        names += [r["name"] for r in d["cases"] if r["name"] not in names]
    for name in names:
        cells, later = [], ""
        for d in summaries:
            r = next((r for r in d["cases"] if r["name"] == name), None)
            if r is None:
                cells += ["not run", "not run"]
                continue
            later = later or rerun_mark(d, r)
            mark = ("!" if r["runs_passed"] != r["runs"] else "") + \
                   ("f" if r["format_passed"] != r["format_total"] else "")
            cells += [f"{num(r['score'])} ({r['runs_passed']}/{r['runs']}){' ' + mark if mark else ''}",
                      num(r["baseline"])]
        lines.append(f"| {name}{later} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Summarise claude plugin eval runs.")
    parser.add_argument("run", type=Path, nargs="+",
                        help="run JSON (--json output, aggregate-result.json, or a saved summary); "
                             "several files print a per-model comparison")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if any behaviour or format check failed in the skill arm")
    parser.add_argument("--save", type=Path, metavar="SUMMARY.json",
                        help="also write a compact summary that is safe to commit (one input file only)")
    parser.add_argument("--update", action="store_true",
                        help="with --save: keep the existing summary and replace only the cases in this run")
    parser.add_argument("--model", help="model id to record when no transcript is left to read it from")
    args = parser.parse_args()
    if args.save and len(args.run) > 1:
        sys.exit("error: --save takes one input file")
    if args.update and not args.save:
        sys.exit("error: --update needs --save")

    summaries = [load(path, args.model) for path in args.run]
    if args.save:
        if not summaries[0]["model"]:
            sys.exit("error: model unknown; no transcript left to read it from. Pass --model.")
        if args.update:
            summaries[0] = merge(json.loads(args.save.read_text(encoding="utf-8")), summaries[0])
        args.save.parent.mkdir(parents=True, exist_ok=True)
        args.save.write_text(json.dumps(summaries[0], indent=2) + "\n", encoding="utf-8")

    all_totals = [totals(d) for d in summaries]
    if len(summaries) == 1:
        print(table(summaries[0]))
    else:
        print(comparison(summaries))
        print()
        print("Cells: behaviour score (runs that passed every behaviour check / runs). "
              "`!` marks a failed behaviour check, `f` a failed format check.")
    if any(rerun_mark(d, r) for d in summaries for r in d["cases"]):
        if len(summaries) == 1:
            print()
        print("`*` marks a case that was run again on its own after the full run.")
    for data, t in zip(summaries, all_totals):
        print()
        describe(data, t)

    failed = False
    for data, t in zip(summaries, all_totals):
        for e in t["errors"]:
            print(f"run error ({data['model']}): {e}", file=sys.stderr)
        if not t["runs"]:
            print("error: a run holds no cases; did the --case pattern match anything?", file=sys.stderr)
            failed = True
        if t["errors"] or data["partial"] or t["runs_passed"] != t["runs"] or t["format_passed"] != t["format_total"]:
            failed = True
    if args.check and failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
