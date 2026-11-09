# Compatibility

The skill is one `SKILL.md` plus one Codex policy file. All three supported
tools load the same folder, `skills/prompt-refiner/`.

| Tool | Checked against | Explicit-only through | Invoke with |
|---|---|---|---|
| Claude Code | 2.1.319 | `disable-model-invocation: true` | `/prompt-refiner` (manual install) or `/prompt-refiner:prompt-refiner` (plugin) |
| OpenCode | 2.2.6 | `metadata.opencode/autoinvoke: "false"`, with `disable-model-invocation` as fallback | `/prompt-refiner` |
| Codex | CLI 0.166.0 | `agents/openai.yaml`: `policy.allow_implicit_invocation: false` | `$prompt-refiner` |

"Explicit-only" means the skill is not offered to the model as something it may
start on its own. It runs only when you call it.

## Frontmatter keys

| Key | Claude Code | OpenCode | Codex |
|---|---|---|---|
| `name`, `description` | Used | Used | Used |
| `disable-model-invocation: true` | Disables auto-invocation | Fallback when `opencode/autoinvoke` is absent | Ignored |
| `metadata.opencode/autoinvoke: "false"` | Ignored | Disables auto-invocation (read first) | Ignored |
| `argument-hint` | Autocomplete hint | Ignored | Ignored |
| `license`, `compatibility`, `metadata.version` | Metadata | Ignored | Tolerated |

Codex's own skill-creator linter (`quick_validate.py`) lists only `name`,
`description`, `license`, `allowed-tools`, and `metadata` as allowed keys and
would flag the others. The Codex loader itself accepts them; this was checked
with `codex debug prompt-input`.

## Files each tool reads

- **Claude Code** loads `SKILL.md`. As a plugin it also reads
  `.claude-plugin/plugin.json`, whose `icon` points to `assets/icon.png`.
- **OpenCode** scans its skill folders and stops descending once it finds a
  `SKILL.md`, so `agents/` is never registered as a skill. Folders whose names
  start with a dot are skipped.
- **Codex** loads `SKILL.md` and `agents/openai.yaml`, which also sets the
  icons from `assets/`.

`evals/`, `docs/`, and the repository files sit outside the skill folder and
are never installed.

## Sharing one install between tools

OpenCode also scans `.claude` and `.agents` skill folders. With the links from
the README (`~/.claude/skills/prompt-refiner` and
`~/.agents/skills/prompt-refiner`), OpenCode finds the skill twice under the
same name and lists it once, Claude Code uses the first link, and Codex uses
the second.

## Other hosts

The instructions are plain Markdown, so any host that supports Agent Skills can
load them. Check that the host cannot auto-invoke the skill, because Run mode
acts on the request.
