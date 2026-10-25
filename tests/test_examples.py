from pathlib import Path

from tastelint.engine import scan_path
from tastelint.extract import document_from_source
from tastelint.rules import RULES

ROOT = Path(__file__).resolve().parents[1]


def test_sloppy_landing_hits_every_rule():
    report = scan_path(ROOT / "examples" / "sloppy-landing", target="examples/sloppy-landing")
    found = {finding.rule_id for finding in report.findings}
    missing = {spec.id for spec in RULES} - found
    assert not missing
    assert report.score < 90
    assert report.file_count == 5


def test_quiet_studio_scores_100():
    report = scan_path(ROOT / "examples" / "quiet-studio", target="examples/quiet-studio")
    leftover = [(finding.rule_id, finding.path, finding.line, finding.snippet) for finding in report.findings]
    assert leftover == []
    assert report.score == 100
    assert report.file_count == 2


def test_hero_tsx_keeps_its_class_string():
    text = (ROOT / "examples" / "sloppy-landing" / "Hero.tsx").read_text(encoding="utf-8")
    doc = document_from_source("Hero.tsx", text)
    section = next(element for element in doc.walk() if element.tag == "section")
    assert "from-purple-500" in section.classes
    assert "min-h-screen" in section.classes
    assert any(element.tag == "button" and element.full_text() == "Get Started" for element in doc.walk())
