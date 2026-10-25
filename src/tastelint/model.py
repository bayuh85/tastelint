"""Shared records for a tastelint run."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    hint: str
    path: str
    line: int
    column: int
    snippet: str


@dataclass
class Report:
    target: str
    findings: list[Finding]
    score: int
    file_count: int
    fail_under: int | None
    breakdown: list[dict] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        if self.fail_under is None:
            return True
        return self.score >= self.fail_under
