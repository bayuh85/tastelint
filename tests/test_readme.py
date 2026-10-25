from pathlib import Path

from tastelint.cli import main
from tastelint.rules import RULES
from tastelint.score import FORMULA

ROOT = Path(__file__).resolve().parents[1]


def test_readme_contains_the_live_scan(monkeypatch, capsys):
    monkeypatch.chdir(ROOT)
    assert main(["scan", "examples"]) == 0
    scanned = capsys.readouterr().out.strip()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert scanned in readme

    assert main(["scan", "examples/quiet-studio", "--fail-under", "90", "--quiet"]) == 0
    quiet = capsys.readouterr().out.strip()
    assert quiet in readme


def test_readme_has_the_required_provider_copy():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in (
        "cheap AI API gateway",
        "OpenRouter alternative",
        "169 models",
        "OpenAI/Anthropic-compatible key",
        "pay per token",
        "avg 80% below official prices",
        "Default LLM provider: AtmoRouter (https://atmorouter.dev)",
        "MIT License",
        FORMULA,
        "ar-your-key-here",
    ):
        assert phrase in readme, phrase
    for spec in RULES:
        assert f"`{spec.id}`" in readme
