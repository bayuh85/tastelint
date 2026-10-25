from tastelint.model import Finding
from tastelint.score import FORMULA, PENALTY, RULE_CAP, breakdown, taste_score


def _finding(rule_id: str, severity: str, line: int = 1) -> Finding:
    return Finding(rule_id, severity, "m", "h", "a.html", line, 1, "snippet")


def test_formula_constants():
    assert PENALTY == {"high": 12, "medium": 5, "low": 2}
    assert RULE_CAP == 12
    assert "12" in FORMULA and "capped at 12" in FORMULA


def test_one_high_and_one_low():
    findings = [
        _finding("gradient-wash", "high"),
        _finding("gradient-wash", "high", line=2),
        _finding("hype-phrase", "high"),
        _finding("empty-cta", "low"),
    ]
    assert taste_score(findings) == 74
    rows = {row["rule_id"]: row["penalty"] for row in breakdown(findings)}
    assert rows["gradient-wash"] == 12
    assert rows["hype-phrase"] == 12
    assert rows["empty-cta"] == 2


def test_medium_cap_stops_at_two():
    findings = [_finding("radius-inflation", "medium", line=i) for i in range(1, 4)]
    rows = breakdown(findings)
    assert rows[0]["findings"] == 3
    assert rows[0]["penalty"] == 10
    assert taste_score(findings) == 90


def test_empty_is_perfect():
    assert taste_score([]) == 100
