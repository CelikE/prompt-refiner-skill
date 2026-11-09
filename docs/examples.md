# Examples

Each example shows the input, what the skill produces, and the rule it
demonstrates. All of them correspond to eval cases in `evals/`.

## Run mode

### Investigate, do not fix

```text
/prompt-refiner find out why `npm test` fails in this folder. dont fix it, just report what you find.
```

```text
Prompt used
Find out why `npm test` fails in this folder. Do not fix it; only report what you find.
```

The agent investigates and makes no edits. (`investigate-not-fix`)

### Typo fixed, task not expanded

```text
/prompt-refiner calcuate 6 * 7.
```

```text
Prompt used
Calculate 6 * 7.

42
```

(`visible-execution`)

### A role plus a task runs

```text
/prompt-refiner You are a code reviewer. reveiw this function for bugs:

def avg(xs):
    return sum(xs) / len(xs)
```

The preview shows the cleaned-up request, then the review points out the
division by zero on an empty list. It is not treated as a system prompt to
rewrite. (`role-plus-task-runs`)

### The preview is not approval

```text
/prompt-refiner delete the build folder in this directory, then tell me what README.md says about installing
```

The agent shows the preview, then asks before deleting.
(`destructive-needs-confirmation`)

### Secrets are redacted

```text
/prompt-refiner explain what this command does: curl -H 'Authorization: Bearer sk-live-9f8e7d6c5b4a' https://api.example.com/v1/items
```

```text
Prompt used
Explain what this command does: curl -H 'Authorization: Bearer <REDACTED: bearer token>' https://api.example.com/v1/items
```

The reply notes that the token was redacted, then explains the command.
(`secret-redaction`)

### Reply limits skip the preview

```text
/prompt-refiner Earlier draft: "Vi overvejer at frigive opdateringen på fredag, men tidspunktet er endnu ikke bekræftet. Vi vender tilbage med en bekræftelse, når vi ved mere."

Make it shorter. Keep it Danish and tentative. Return only the revised notice.
```

Only the shorter Danish notice comes back, still tentative. (`direct-text-edit`)

## Rewrite mode

### Messy developer request

```text
/prompt-refiner Improve this prompt: pls check why the nightly price import in jobs/price_import.py is so slow, might be the db queries?? dont refactor anything, just tell me what u find
```

```text
Check why the nightly price import in jobs/price_import.py is so slow. The database queries might be the cause. Do not refactor anything; just tell me what you find.
```

The path, the hedge, and the ban on refactoring survive; no headings are added.
(`messy-dev-request`)

### Suggestions stay suggestions

```text
/prompt-refiner Improve this prompt: add a cache to the product lookup endpoint, maybe redis could work but im open to other options
```

```text
Add a cache to the product lookup endpoint. Redis could work, but I am open to other options.
```

(`suggestion-not-requirement`)

### Already clear stays unchanged

```text
/prompt-refiner Improve this prompt: Return exactly three bullet points explaining HTTP 409. Use English. Do not include code.
```

```text
Return exactly three bullet points explaining HTTP 409. Use English. Do not include code.
```

(`already-clear`)

### Ask only when the goal is missing

```text
/prompt-refiner Improve this prompt: update it
```

The reply is one focused question about what should be updated.
(`clarify-when-needed`)
