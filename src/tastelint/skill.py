"""Install tastelint guidance where coding agents look for it."""

from __future__ import annotations

from pathlib import Path

from tastelint.charter import principles_markdown
from tastelint.rules import RULES

TARGETS = ("claude", "cursor", "codex")
START = "<!-- tastelint:start -->"
END = "<!-- tastelint:end -->"


def guidance_body() -> str:
    lines = [principles_markdown(), "", "## When you change UI", ""]
    lines.append("Before you finish an interface change, run:")
    lines.append("")
    lines.append("```bash")
    lines.append("tastelint scan <path> --fail-under 90")
    lines.append("```")
    lines.append("")
    lines.append(
        "Read every high finding and fix it in the file the report names. "
        "If `ATMOROUTER_API_KEY` is set, also run `tastelint review <path>` and apply "
        "the edits that name a file and a replacement."
    )
    lines.append("")
    lines.append(
        "Reject any suggestion, including one from a review model, that adds a violet "
        "or indigo gradient, the Inter typeface, a glass panel, emoji headings, or a "
        "row of three equal cards."
    )
    lines.append("")
    lines.append("## Rules the scanner enforces")
    lines.append("")
    for spec in RULES:
        lines.append(f"- `{spec.id}` ({spec.severity}) — {spec.summary} {spec.hint}")
    lines.append("")
    lines.append(
        "A line can opt out with `tastelint-disable-line <rule-id>` or "
        "`tastelint-disable-next-line <rule-id>`. Use that for a deliberate exception, "
        "not as the default."
    )
    lines.append("")
    return "\n".join(lines)


def _claude(root: Path) -> Path:
    path = root / ".claude" / "skills" / "tastelint" / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "---\n"
        "name: tastelint\n"
        "description: Run the tastelint taste linter and follow the Plain Surface Charter when creating or editing interface code.\n"
        "---\n\n"
        + guidance_body()
    )
    path.write_text(content, encoding="utf-8")
    return path


def _cursor(root: Path) -> Path:
    path = root / ".cursor" / "rules" / "tastelint.mdc"
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "---\n"
        "description: Plain Surface Charter for UI edits. Run tastelint and refuse generic generated styling.\n"
        'globs: "**/*.{html,htm,css,scss,jsx,tsx,vue,svelte,mdx}"\n'
        "alwaysApply: false\n"
        "---\n\n"
        + guidance_body()
    )
    path.write_text(content, encoding="utf-8")
    return path


def _upsert_agents(path: Path, body: str) -> None:
    block = f"{START}\n{body.rstrip()}\n{END}\n"
    if not path.exists():
        path.write_text("# Agent notes\n\n" + block, encoding="utf-8")
        return
    text = path.read_text(encoding="utf-8")
    if START in text and END in text:
        pre, rest = text.split(START, 1)
        _, post = rest.split(END, 1)
        path.write_text(pre + block + post.lstrip("\n"), encoding="utf-8")
        return
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_text(text + "\n" + block, encoding="utf-8")


def _codex(root: Path) -> Path:
    path = root / "AGENTS.md"
    section = "## Plain Surface Charter (tastelint)\n\n" + guidance_body()
    _upsert_agents(path, section)
    return path


def install(target: str, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    if target == "claude":
        return _claude(dest)
    if target == "cursor":
        return _cursor(dest)
    if target == "codex":
        return _codex(dest)
    raise ValueError(f"unknown target: {target}")


def display(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
