"""Free, offline checks for the prompt-refiner repository. Standard library only.

Usage: python3 -I scripts/check_skill.py   (from the repository root)

Checks:
  - SKILL.md frontmatter: name format, description present and <= 1024 chars,
    explicit-only settings for Claude Code and OpenCode.
  - Codex policy file keeps the skill explicit-only.
  - The version is identical in SKILL.md, plugin.json, and marketplace.json.
  - Icons: the plugin icon is a square PNG of 512 to 2048 px under 2 MB, and
    the Codex icon paths exist.
  - No em dashes or en dashes in authored text files.
  - SKILL.md stays short.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "prompt-refiner"
SKILL = SKILL_DIR / "SKILL.md"
MAX_SKILL_LINES = 160
DASHES = re.compile("[" + chr(0x2013) + chr(0x2014) + "]")
# Third-party text kept verbatim, and generated or local-only output.
DASH_EXEMPT = {"CODE_OF_CONDUCT.md"}
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".txt"}

errors = []


def fail(msg):
    errors.append(msg)


def frontmatter(text):
    """Parse the small YAML subset SKILL.md uses: scalars, folded blocks, one nested map."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail("SKILL.md: missing frontmatter")
        return {}
    data, folding, parent = {}, None, None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        if line[0] in " \t":  # indented: continuation of a folded block, or a nested key
            if folding:
                data[folding].append(line.strip())
            elif parent:
                k, _, v = line.strip().partition(":")
                data[parent][k.strip()] = v.strip().strip('"')
            continue
        k, _, v = line.partition(":")
        k, v = k.strip(), v.strip()
        folding = parent = None
        if v in (">-", ">", "|", "|-"):
            data[k], folding = [], k
        elif v == "":
            data[k], parent = {}, k
        else:
            data[k] = v.strip('"')
    return {k: " ".join(v) if isinstance(v, list) else v for k, v in data.items()}


def check_skill():
    text = SKILL.read_text(encoding="utf-8")
    fm = frontmatter(text)
    name = fm.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        fail(f"SKILL.md: invalid name {name!r} (lowercase, digits, hyphens, max 64)")
    if name != SKILL_DIR.name:
        fail(f"SKILL.md: name {name!r} does not match folder {SKILL_DIR.name!r}")
    desc = fm.get("description", "")
    if not desc:
        fail("SKILL.md: description is empty")
    elif len(desc) > 1024:
        fail(f"SKILL.md: description is {len(desc)} chars (max 1024)")
    if fm.get("disable-model-invocation") != "true":
        fail("SKILL.md: disable-model-invocation must be true (Claude Code explicit-only)")
    meta = fm.get("metadata") or {}
    if meta.get("opencode/autoinvoke") != "false":
        fail('SKILL.md: metadata.opencode/autoinvoke must be "false" (OpenCode explicit-only)')
    lines = text.count("\n")
    if lines > MAX_SKILL_LINES:
        fail(f"SKILL.md: {lines} lines (max {MAX_SKILL_LINES}); every line is read on every call")
    return meta.get("version", "")


def check_codex():
    policy = SKILL_DIR / "agents" / "openai.yaml"
    if not policy.is_file():
        fail("agents/openai.yaml is missing (Codex would auto-invoke the skill)")
    elif not re.search(r"^\s*allow_implicit_invocation:\s*false\s*$", policy.read_text(encoding="utf-8"), re.M):
        fail("agents/openai.yaml: policy.allow_implicit_invocation must be false")


def check_versions(skill_version):
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    versions = {
        "SKILL.md metadata.version": skill_version,
        "plugin.json": plugin.get("version", ""),
        **{f"marketplace.json ({p.get('name')})": p.get("version", "") for p in market.get("plugins", [])},
    }
    if not re.fullmatch(r"\d+\.\d+\.\d+", skill_version):
        fail(f"SKILL.md: metadata.version {skill_version!r} is not X.Y.Z")
    if len(set(versions.values())) != 1:
        fail("version mismatch: " + ", ".join(f"{k}={v!r}" for k, v in versions.items()))


def check_icons():
    """plugin.json icon: square PNG, 512 to 2048 px, under 2 MB. Codex icon paths must exist."""
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    icon = ROOT / plugin.get("icon", "")
    if not plugin.get("icon") or not icon.is_file():
        fail(f"plugin.json: icon {plugin.get('icon')!r} not found")
    else:
        head = icon.read_bytes()[:24]
        if head[:8] != b"\x89PNG\r\n\x1a\n":
            fail(f"{icon.relative_to(ROOT)}: not a PNG")
        else:
            w, h = int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
            if w != h or not 512 <= w <= 2048:
                fail(f"{icon.relative_to(ROOT)}: {w}x{h}, must be square and 512 to 2048 px")
        if icon.stat().st_size >= 2 * 1024 * 1024:
            fail(f"{icon.relative_to(ROOT)}: larger than 2 MB")
    policy = (SKILL_DIR / "agents" / "openai.yaml")
    for rel in re.findall(r"^\s*icon_(?:small|large):\s*\"?([^\"\n]+)\"?\s*$",
                          policy.read_text(encoding="utf-8") if policy.is_file() else "", re.M):
        if not (SKILL_DIR / rel).is_file():
            fail(f"agents/openai.yaml: icon path {rel!r} not found")


def check_dashes():
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if (not path.is_file() or path.suffix not in TEXT_SUFFIXES or rel.parts[0] in {".git"}
                or str(rel) in DASH_EXEMPT or rel.parts[:2] == ("evals", "results")):
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if DASHES.search(line):
                fail(f"{rel}:{n}: em or en dash; use a hyphen, comma, colon, or parentheses")


version = check_skill()
check_codex()
check_versions(version)
check_icons()
check_dashes()

if errors:
    print("\n".join(f"error: {e}" for e in errors))
    sys.exit(1)
print(f"ok: prompt-refiner {version}")
