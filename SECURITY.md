# Security policy

## Supported versions

Only the latest release receives fixes.

## Threat model

prompt-refiner runs inside a coding agent that can read files, run commands,
and send messages. The skill makes these promises:

1. **The outer request picks the mode.** Text inside the material being refined
   (pasted prompts, logs, emails, web pages) cannot switch from Rewrite to Run.
2. **Rewrite mode uses no tools.** Paths, URLs, and commands in the material are
   treated as text.
3. **Run mode grants nothing new.** Instructions inside pasted or quoted
   material are treated as part of the material, not as requests from you. The
   agent's normal permission and confirmation rules still apply.
4. **The preview is not approval.** Destructive, irreversible, or
   outward-facing steps still need confirmation.
5. **Secrets are redacted** in the preview and kept out of the rest of the
   reply.
6. **No auto-invocation.** The skill is configured explicit-only in every
   supported tool.

The skill is a set of instructions, not a sandbox. It reduces risk; it does not
replace your agent's permission settings.

## What counts as a vulnerability

- Embedded text that makes the skill execute instead of rewrite, or use tools in
  Rewrite mode.
- In Run mode, an instruction inside pasted material being carried out as if you
  had asked for it.
- A secret from the request appearing unredacted in the preview or elsewhere
  in the reply.
- The preview being treated as approval for a destructive action.
- A configuration in this repository that lets a supported tool auto-invoke the
  skill.

Poor refinements (wrong wording, lost nuance) are bugs, not vulnerabilities.
Report them with the "Misrefinement" issue template.

## Reporting

Use GitHub's private vulnerability reporting:
**Security** tab, then **Report a vulnerability**. Do not open a public issue.

Include the exact input, the tool and its version, the model, and what
happened. You can expect an acknowledgement within 7 days.
