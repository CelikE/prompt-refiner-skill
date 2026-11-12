"""Copy the per-run transcripts of an eval run next to its results.

Usage: python3 -I scripts/collect_traces.py RUN.json [DEST]

`claude plugin eval` writes each run's transcript to a temporary directory and
deletes it afterwards, so a failed or surprising run cannot be inspected later.
Run the suite with --keep-temp, then run this script: it copies every
transcript named in RUN.json to DEST/<case>/<arm>-<n>.jsonl (default DEST: a
`traces` directory beside RUN.json).

Transcripts can contain local paths and account details. evals/results/ is
ignored by Git; keep them out of commits and issues.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Collect eval transcripts kept by --keep-temp.")
    parser.add_argument("run", type=Path, help="run JSON (--json output or aggregate-result.json)")
    parser.add_argument("dest", type=Path, nargs="?", help="target directory (default: traces/ beside RUN.json)")
    args = parser.parse_args()

    data = json.loads(args.run.read_text(encoding="utf-8"))
    dest = args.dest or args.run.parent / "traces"
    copied, missing = 0, []
    for case in data["cases"]:
        for arm, runs in case["arms"].items():
            for n, run in enumerate(runs or [], 1):
                src = Path(run.get("tracePath") or "")
                target = dest / case["name"] / f"{arm}-{n}.jsonl"
                if not src.is_file():
                    missing.append(f"{case['name']} {arm}-{n}")
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, target)
                copied += 1
    print(f"copied {copied} transcripts to {dest}")
    if missing:
        print(f"error: {len(missing)} transcripts not found (was the suite run with --keep-temp?): "
              + ", ".join(missing[:5]) + (" ..." if len(missing) > 5 else ""), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
