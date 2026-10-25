from tastelint.engine import scan_path


def test_disable_next_line_and_same_line(tmp_path):
    page = tmp_path / "page.html"
    page.write_text(
        "<!-- tastelint-disable-next-line hype-phrase -->\n"
        "<h1>Unlock the power of clay</h1>\n"
        "<p>Supercharge the glaze. <!-- tastelint-disable-line hype-phrase --></p>\n"
        "<p>Reimagine the shelf.</p>\n",
        encoding="utf-8",
    )
    report = scan_path(page, target="page.html")
    hype_lines = [finding.line for finding in report.findings if finding.rule_id == "hype-phrase"]
    assert hype_lines == [4]


def test_node_modules_are_skipped(tmp_path):
    vendor = tmp_path / "node_modules"
    vendor.mkdir()
    (vendor / "Bad.tsx").write_text("<h1>🚀 Unlock the power</h1>", encoding="utf-8")
    (tmp_path / "Ok.html").write_text("<p>Twelve slots on Monday.</p>", encoding="utf-8")
    report = scan_path(tmp_path, target="sample")
    assert report.file_count == 1
    assert report.findings == []
    assert report.score == 100


def test_missing_extension_is_ignored(tmp_path):
    (tmp_path / "notes.txt").write_text("Unlock the power of notes", encoding="utf-8")
    report = scan_path(tmp_path, target="notes")
    assert report.file_count == 0
    assert report.score == 100


def test_mdx_copy_is_scanned(tmp_path):
    page = tmp_path / "page.mdx"
    page.write_text("# Unlock the power of widgets\n", encoding="utf-8")
    report = scan_path(page, target="page.mdx")
    assert any(finding.rule_id == "hype-phrase" for finding in report.findings)
