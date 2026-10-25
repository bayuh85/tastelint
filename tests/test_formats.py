import json

from tastelint.engine import scan_path
from tastelint.formatters import format_json, format_sarif, format_text
from tastelint.rules import RULES


def test_text_json_and_sarif(tmp_path):
    page = tmp_path / "page.html"
    page.write_text("<h1>🚀 Unlock the power of widgets</h1>\n", encoding="utf-8")
    report = scan_path(page, fail_under=90, target="page.html")
    text = format_text(report)
    assert "taste score" in text
    assert "hype-phrase" in text
    assert "gate: 90  ·  fail" in text
    assert report.passed is False

    payload = json.loads(format_json(report))
    assert payload["tool"] == "tastelint"
    assert payload["score"] == report.score
    assert payload["fail_under"] == 90
    assert payload["passed"] is False
    assert {item["rule_id"] for item in payload["findings"]} >= {"hype-phrase", "emoji-heading"}

    sarif = json.loads(format_sarif(report))
    assert sarif["version"] == "2.1.0"
    driver = sarif["runs"][0]["tool"]["driver"]
    assert driver["name"] == "tastelint"
    assert {rule["id"] for rule in driver["rules"]} == {spec.id for spec in RULES}
    results = sarif["runs"][0]["results"]
    assert results
    assert results[0]["locations"][0]["physicalLocation"]["region"]["startLine"] >= 1
    high = next(item for item in results if item["ruleId"] == "hype-phrase")
    assert high["level"] == "error"
