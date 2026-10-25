"""Taste score.

High findings cost 12, medium 5, low 2, and each rule is capped at 12.
Penalties for one rule are applied largest-first until the cap. The score
is 100 minus the sum of those capped penalties, and it does not go below 0.
"""

from __future__ import annotations

from tastelint.model import Finding

PENALTY = {"high": 12, "medium": 5, "low": 2}
RULE_CAP = 12
FORMULA = "High findings cost 12, medium 5, low 2, and each rule is capped at 12."


def breakdown(findings: list[Finding]) -> list[dict]:
    grouped: dict[str, list[int]] = {}
    for finding in findings:
        grouped.setdefault(finding.rule_id, []).append(PENALTY[finding.severity])
    rows = []
    for rule_id in sorted(grouped):
        penalties = sorted(grouped[rule_id], reverse=True)
        acc = 0
        for penalty in penalties:
            if acc + penalty > RULE_CAP:
                continue
            acc += penalty
        rows.append({"rule_id": rule_id, "findings": len(penalties), "penalty": acc})
    rows.sort(key=lambda row: (-row["penalty"], row["rule_id"]))
    return rows


def taste_score(findings: list[Finding]) -> int:
    total = sum(row["penalty"] for row in breakdown(findings))
    return max(0, 100 - total)
