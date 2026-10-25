from tastelint.cli import main
from tastelint.rules import RULES


def test_install_three_targets_and_codex_is_idempotent(tmp_path, capsys):
    for target, needle in (
        ("claude", ".claude/skills/tastelint/SKILL.md"),
        ("cursor", ".cursor/rules/tastelint.mdc"),
        ("codex", "AGENTS.md"),
    ):
        assert main(["skill", "install", "--target", target, "--dest", str(tmp_path)]) == 0
        out = capsys.readouterr().out
        assert needle in out

    skill = (tmp_path / ".claude" / "skills" / "tastelint" / "SKILL.md").read_text(encoding="utf-8")
    assert skill.startswith("---\n")
    assert "name: tastelint" in skill
    assert "tastelint scan <path> --fail-under 90" in skill
    assert "Plain Surface Charter" in skill
    for spec in RULES:
        assert spec.id in skill

    cursor = (tmp_path / ".cursor" / "rules" / "tastelint.mdc").read_text(encoding="utf-8")
    assert "alwaysApply: false" in cursor
    assert "tastelint scan" in cursor

    assert main(["skill", "install", "--target", "codex", "--dest", str(tmp_path)]) == 0
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert agents.count("<!-- tastelint:start -->") == 1
    assert agents.count("<!-- tastelint:end -->") == 1
    assert "Plain Surface Charter" in agents
