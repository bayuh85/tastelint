"""Text, JSON, and SARIF renderers. Output is deterministic."""

from __future__ import annotations

import json

from tastelint import __version__
from tastelint.model import Report
from tastelint.rules import RULES
from tastelint.score import FORMULA

_SARIF_LEVEL = {"high": "error", "medium": "warning", "low": "note"}


def _plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def format_text(report: Report, verbose: bool = False, quiet: bool = False) -> str:
    highs = sum(1 for finding in report.findings if finding.severity == "high")
    mediums = sum(1 for finding in report.findings if finding.severity == "medium")
    lows = sum(1 for finding in report.findings if finding.severity == "low")
    lines = [
        f"tastelint {__version__}",
        (
            f"{report.target}  ·  {_plural(report.file_count, 'file')}  ·  "
            f"{_plural(len(report.findings), 'finding')} "
            f"({highs} high, {mediums} medium, {lows} low)  ·  "
            f"taste score {report.score}/100"
        ),
        "",
    ]
    if report.file_count == 0:
        lines.append("No HTML, CSS, or component files found.")
        lines.append("")
    if not quiet:
        for finding in report.findings:
            lines.append(
                f"{finding.path}:{finding.line}  {finding.severity:<6}  "
                f"{finding.rule_id:<16}  {finding.message}"
            )
            if verbose:
                lines.append(f"  hint: {finding.hint}")
                if finding.snippet:
                    lines.append(f"  > {finding.snippet}")
        if report.findings:
            lines.append("")
    if report.fail_under is None:
        lines.append("gate: not set")
    else:
        state = "pass" if report.passed else "fail"
        lines.append(f"gate: {report.fail_under}  ·  {state}")
    lines.append("")
    return "\n".join(lines)


def format_json(report: Report) -> str:
    payload = {
        "tool": "tastelint",
        "version": __version__,
        "target": report.target,
        "score": report.score,
        "file_count": report.file_count,
        "finding_count": len(report.findings),
        "fail_under": report.fail_under,
        "passed": report.passed,
        "formula": FORMULA,
        "breakdown": report.breakdown,
        "findings": [
            {
                "rule_id": finding.rule_id,
                "severity": finding.severity,
                "message": finding.message,
                "hint": finding.hint,
                "path": finding.path,
                "line": finding.line,
                "column": finding.column,
                "snippet": finding.snippet,
            }
            for finding in report.findings
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def format_sarif(report: Report) -> str:
    rules = [
        {
            "id": spec.id,
            "shortDescription": {"text": spec.summary},
            "fullDescription": {"text": spec.summary},
            "help": {"text": spec.hint},
            "defaultConfiguration": {"level": _SARIF_LEVEL[spec.severity]},
        }
        for spec in RULES
    ]
    results = []
    for finding in report.findings:
        results.append(
            {
                "ruleId": finding.rule_id,
                "level": _SARIF_LEVEL[finding.severity],
                "message": {"text": finding.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": finding.path},
                            "region": {
                                "startLine": finding.line,
                                "startColumn": finding.column,
                            },
                        }
                    }
                ],
                "properties": {"severity": finding.severity, "hint": finding.hint},
            }
        )
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "tastelint",
                        "version": __version__,
                        "rules": rules,
                    }
                },
                "properties": {"tasteScore": report.score, "formula": FORMULA},
                "results": results,
            }
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def render(report: Report, kind: str, verbose: bool = False, quiet: bool = False) -> str:
    if kind == "json":
        return format_json(report)
    if kind == "sarif":
        return format_sarif(report)
    return format_text(report, verbose=verbose, quiet=quiet)
