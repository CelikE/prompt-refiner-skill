# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
