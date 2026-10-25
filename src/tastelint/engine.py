"""Run the rule set over a file or a directory."""

from __future__ import annotations

import re
from pathlib import Path

from tastelint.discover import discover, display_path
from tastelint.extract import build_project, load_document
from tastelint.model import Finding, Report
from tastelint.rules import run_rules
from tastelint.score import breakdown, taste_score


def _ids(text: str, kind: str) -> set[str]:
    if kind == "next":
        pattern = r"tastelint-disable-next-line\s+([^\n]+)"
    elif kind == "line":
        pattern = r"tastelint-disable-line\s+([^\n]+)"
    else:
        pattern = r"tastelint-disable(?!-)\s+([^\n]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return set()
    raw = re.split(r"\*/|-->", match.group(1))[0]
    return {part.lower() for part in re.split(r"[\s,]+", raw.strip()) if part}


def _suppressed(lines: list[str], finding: Finding) -> bool:
    line = finding.line
    if 1 <= line <= len(lines):
        ids = _ids(lines[line - 1], "line") | _ids(lines[line - 1], "bare")
        if "all" in ids or finding.rule_id in ids:
            return True
    if line >= 2:
        ids = _ids(lines[line - 2], "next")
        if "all" in ids or finding.rule_id in ids:
            return True
    return False


def scan_path(path: Path | str, fail_under: int | None = None, target: str | None = None) -> Report:
    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(root)
    documents = [load_document(file, display_path(file)) for file in discover(root)]
    project = build_project(documents)
    by_path = {doc.path: doc for doc in documents}
    findings: list[Finding] = []
    for doc in documents:
        for finding in run_rules(doc, project):
            if not _suppressed(by_path[finding.path].lines, finding):
                findings.append(finding)
    findings.sort(key=lambda item: (item.path, item.line, item.column, item.rule_id))
    rows = breakdown(findings)
    shown = target if target is not None else display_path(root)
    return Report(
        target=shown,
        findings=findings,
        score=taste_score(findings),
        file_count=len(documents),
        fail_under=fail_under,
        breakdown=rows,
    )
