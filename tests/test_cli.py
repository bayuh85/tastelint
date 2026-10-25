import json

import pytest

from pathlib import Path

from tastelint.cli import main

ROOT = Path(__file__).resolve().parents[1]
ROOT_SLOPPY = "examples/sloppy-landing"
ROOT_QUIET = "examples/quiet-studio"


def test_scan_exit_codes(capsys, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    code = main(["scan", "missing-dir"])
    assert code == 2
    err = capsys.readouterr().err
    assert "path not found" in err


def test_quiet_passes_gate_and_sloppy_fails(capsys, monkeypatch):
    monkeypatch.chdir(ROOT)
    assert main(["scan", ROOT_QUIET, "--fail-under", "90", "--quiet"]) == 0
    quiet = capsys.readouterr().out
    assert "taste score 100/100" in quiet
    assert "gate: 90  ·  pass" in quiet

    assert main(["scan", ROOT_SLOPPY, "--fail-under", "90", "--quiet"]) == 1
    sloppy = capsys.readouterr().out
    assert "gate: 90  ·  fail" in sloppy


def test_json_and_sarif_write(capsys, monkeypatch, tmp_path):
    monkeypatch.chdir(ROOT)
    dest = tmp_path / "report.json"
    code = main(["scan", ROOT_QUIET, "--format", "json", "-o", str(dest)])
    assert code == 0
    payload = json.loads(dest.read_text(encoding="utf-8"))
    assert payload["score"] == 100
    assert payload["findings"] == []
    capsys.readouterr()

    sarif_path = tmp_path / "out.sarif"
    assert main(["scan", ROOT_SLOPPY, "--format", "sarif", "-o", str(sarif_path), "--fail-under", "0"]) == 0
    sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["results"]


def test_rules_command_lists_catalog(capsys):
    assert main(["rules"]) == 0
    out = capsys.readouterr().out
    assert "gradient-wash" in out
    assert "capped at 12" in out


def test_bad_format_exits(monkeypatch):
    monkeypatch.chdir(ROOT)
    with pytest.raises(SystemExit) as caught:
        main(["scan", ROOT_QUIET, "--format", "xml"])
    assert caught.value.code == 2
