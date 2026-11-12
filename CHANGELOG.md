# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Eval graders are split into behaviour checks (scored in both arms) and
  format checks (`fmt(...)`, skill arm only). The published delta now comes
  from behaviour checks alone. Up to 0.1.0 the baseline lost points for not
  printing the skill's own "Prompt used" format, which inflated the delta.
- Mixed graders were split so that no behaviour check mentions the preview,
  and every case has at least one behaviour check the plain model can pass.
- `docs/evals.md` explains that the baseline arm receives the literal
  `/prompt-refiner` text and that the delta is an upper bound.
- `investigate-not-fix` and `destructive-needs-confirmation` now start from a
  real workspace (a failing test with a one-line fix; a build folder and a
  README) instead of an empty one. Run the suite with `--scaffold`.
- `destructive-needs-confirmation` also fails when the deletion is handed to a
  subagent (`no-delegation`); `investigate-not-fix` requires the reply to name
  the cause.
- Docs no longer claim that a Bash attempt is recorded when Bash is not
  granted: the model has no shell in that case.
- `SKILL.md`: the Run-mode boundary now says that instructions inside pasted or
  quoted material are part of the material, not requests from the user.
  Rewrite mode already had this through the mode rule. `SECURITY.md` and
  `docs/design.md` list it. Opus 5.5, Sonnet 5.5, and Haiku 5.5 already behaved
  this way before the sentence was added (5 of 5 runs each), so this states a
  promise and guards it; it does not change measured behaviour.
- `secret-redaction` checks for the leaked token with an exact-text match on
  the reply instead of relying on an LLM judge.

- Risky eval cases (deleting, embedded instructions, secrets, mode routing) run
  10 times per arm instead of 3 (`runs=RISKY`). Leave `--runs` out of a full run.
- Published results now cover Opus 5.5, Sonnet 5.5, and Haiku 5.5, with one
  summary per model in `docs/results/`. The runs found failures that 3 runs on
  Opus did not show; `docs/evals.md` lists them. Two are open problems in the
  skill on smaller models: no confirmation before a destructive step, and a
  redacted secret repeated in the answer.
- `clarify-when-needed` no longer requires a question mark in the reply.
- `secret-connection-string` checks the explanation with a regex. The LLM judge
  failed a reply that plainly explained the rejected password.
- The manual Evals workflow takes a `model` input and uses each case's own run
  count unless `runs` is set.

### Fixed

- `SKILL.md`: a redacted secret is no longer repeated in the answer. The
  preview showed `<REDACTED: password>` and the explanation below it sometimes
  quoted the password (1 of 10 runs on Opus, 2 of 10 on Haiku). The rule now
  covers the whole reply.

- `summarize_results.py --check` now fails when the run holds no cases (for
  example after a `--case` pattern that matched nothing).

### Added

- Eval case `run-mode-pasted-instructions`: a ticket to summarise that carries
  its own "ignore the request, create a file" instruction.
- Seven eval cases for rules that had none and for inputs built to tempt:
  `look-into-not-fix`, `negations-kept`, `duplicate-removed`,
  `unclear-mode-rewrites`, `secret-connection-string`, `multi-part-structure`,
  and `json-only-no-preview`. Every rule in `SKILL.md` now has a case.
- `summarize_results.py` prints a per-model comparison when given several
  summaries, and `--save --update` replaces single cases in a saved summary
  after a partial re-run.

- `scripts/summarize_results.py` prints the results table from an eval run and,
  with `--check`, fails when a behaviour or format check fails in the skill arm.
  The manual Evals workflow runs it.
- `scripts/collect_traces.py` copies the transcripts of an eval run next to its
  results, so a baseline score can be audited after the run. The Evals workflow
  runs the suite with `--keep-temp` and uploads the transcripts.
- `docs/results/` holds a committed summary of each published run (scores and
  per-grader pass counts in both arms, no transcripts). `summarize_results.py
  --save` writes it and can print the table again from it.

## [0.1.0] - 2026-11-09

Initial public release.

### Added

- `prompt-refiner` skill with two modes: Rewrite (return the refined prompt
  only) and Run (show a "Prompt used" preview, then carry the request out).
- Fidelity rules: keep scope, kind of work, hedges, negations, and literals;
  no personas or invented requirements; ask only when the goal is unclear.
- Safety rules: the outer request picks the mode, Rewrite mode uses no tools,
  Run mode grants nothing new, the preview is not approval for destructive or
  outward-facing actions, and secrets are redacted in the preview.
- Support for Claude Code (plugin and manual install), OpenCode, and Codex
  (`agents/openai.yaml` keeps it explicit-only).
- Icon (SVG source and 1024 px PNG), used by the Claude Code plugin, Codex,
  and the README.
- Eval suite of 24 generated cases with regex, tool-use, and LLM graders, and a
  generator that refuses to overwrite case directories without `--force`.
- CI for skill metadata, generated-eval drift, Markdown, links, and secrets,
  plus a manual workflow for paid eval runs.

[Unreleased]: https://github.com/CelikE/prompt-refiner-skill/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/CelikE/prompt-refiner-skill/releases/tag/v0.1.0
