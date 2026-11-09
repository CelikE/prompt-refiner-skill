# Contributing

Thanks for helping improve prompt-refiner. The most useful contribution is a
**misrefinement report**: an input where the skill changed your meaning, added
something you did not ask for, or picked the wrong mode. Open one with the
"Misrefinement" issue template; it usually becomes an eval case.

## Ground rule

Every behaviour change to `SKILL.md` comes with an eval case that fails without
the change and passes with it. Wording-only edits that do not change behaviour
need no new case, but the existing suite must still pass.

## Repository layout

| Path | Purpose |
|---|---|
| `skills/prompt-refiner/SKILL.md` | The skill. The only file the model reads. |
| `skills/prompt-refiner/agents/openai.yaml` | Codex policy (explicit-only). |
| `.claude-plugin/` | Claude Code plugin and marketplace manifests. |
| `evals/generate.py` | Source of truth for all eval cases. |
| `evals/<case>/` | Generated. Never edit by hand. |
| `docs/` | Design notes, compatibility, examples, eval results. |
| `scripts/check_skill.py` | Metadata, version, and style checks run by CI. |

## Local setup

Link your clone into the tools you use, so you test your working copy:

```sh
ln -s "$PWD/skills/prompt-refiner" ~/.claude/skills/prompt-refiner
ln -s "$PWD/skills/prompt-refiner" ~/.agents/skills/prompt-refiner
```

## Changing the skill

1. Edit `skills/prompt-refiner/SKILL.md`.
2. Add or update a case in `evals/generate.py` (`case(...)` call).
3. Regenerate the case directories:

   ```sh
   python3 -I evals/generate.py evals --force
   ```

4. Run the affected cases (needs Claude Code and costs API credit):

   ```sh
   claude plugin eval . --case 'your-case-*' --runs 3 --allow-tools Edit Write
   ```

5. Run the free checks:

   ```sh
   python3 -I scripts/check_skill.py
   ```

6. Add an entry under `Unreleased` in `CHANGELOG.md`.

Include the eval output (with and without the skill) in your pull request.

## Writing eval cases

- Prefer cheap, deterministic graders (`rx`, `no_tool`) and use `llm` graders
  for judgement calls.
- Rewrite-mode cases should include `**NO_READ`, so any file access fails.
- Offer a tool in `tools=` when a zero-call check needs it to mean something.
  Do not grant Bash in the run command; the suite relies on it being absent.
- Keep prompts realistic: typos, missing punctuation, mixed instructions.

## Style

- Plain, direct wording. No em dashes or en dashes (U+2014, U+2013);
  `check_skill.py` enforces this.
- Keep `SKILL.md` short. Every line is read on every invocation. Prefer
  sharpening an existing rule to adding a new one.
- Markdown is linted with `markdownlint-cli2` using `.markdownlint-cli2.yaml`.

## Versioning and releases

The project uses [Semantic Versioning](https://semver.org/). While on 0.x:

- **Minor**: a behaviour change (new rule, changed routing) or a newly
  supported tool.
- **Patch**: wording fixes, docs, and new eval cases for existing behaviour.

The version lives in three places that CI keeps in sync:
`skills/prompt-refiner/SKILL.md` (`metadata.version`),
`.claude-plugin/plugin.json`, and `.claude-plugin/marketplace.json`.

Release steps (maintainer):

1. Bump the version in all three files.
2. Move `Unreleased` entries in `CHANGELOG.md` under the new version.
3. Run the "Evals" workflow and update the results in `docs/evals.md`.
4. Tag `vX.Y.Z` and publish a GitHub Release with the changelog section as notes.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
