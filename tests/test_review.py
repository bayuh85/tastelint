import json
import urllib.error
import urllib.request

from tastelint.cli import main


def _silence_network(monkeypatch):
    def explode(*_args, **_kwargs):
        raise AssertionError("network was called")

    monkeypatch.setattr(urllib.request, "urlopen", explode)


def test_dry_run_does_not_call_network(tmp_path, monkeypatch, capsys):
    _silence_network(monkeypatch)
    monkeypatch.delenv("ATMOROUTER_API_KEY", raising=False)
    monkeypatch.delenv("TASTELINT_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    page = tmp_path / "page.html"
    page.write_text("<h1>Unlock the power of widgets</h1>\n", encoding="utf-8")
    code = main(
        [
            "review",
            str(page),
            "--dry-run",
            "--base-url",
            "https://example.test/v1",
            "--model",
            "demo/model",
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "network was not called" in out
    assert "https://example.test/v1/chat/completions" in out
    assert "demo/model" in out
    assert "hype-phrase" in out
    assert "Plain Surface Charter" in out


def test_missing_key_exits_before_network(tmp_path, monkeypatch, capsys):
    _silence_network(monkeypatch)
    monkeypatch.delenv("ATMOROUTER_API_KEY", raising=False)
    monkeypatch.delenv("TASTELINT_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    page = tmp_path / "page.html"
    page.write_text("<p>Unlock the power of widgets</p>\n", encoding="utf-8")
    code = main(["review", str(page)])
    assert code == 4
    err = capsys.readouterr().err
    assert "ATMOROUTER_API_KEY" in err
    assert "atmorouter.dev" in err


def test_clean_file_skips_the_model(tmp_path, monkeypatch, capsys):
    _silence_network(monkeypatch)
    page = tmp_path / "page.html"
    page.write_text("<p>Twelve slots. Bring bone-dry work.</p>\n", encoding="utf-8")
    assert main(["review", str(page), "--fail-under", "90"]) == 0
    assert "Nothing to review" in capsys.readouterr().out


def test_review_posts_a_compact_summary(tmp_path, monkeypatch, capsys):
    page = tmp_path / "page.html"
    page.write_text("<p>Unlock the power of widgets</p>\n", encoding="utf-8")
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps(
                {"choices": [{"message": {"content": "Replace the headline with a specific claim."}}]}
            ).encode()

    def fake_urlopen(req, timeout=0):
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        captured["auth"] = req.get_header("Authorization")
        captured["body"] = json.loads(req.data.decode())
        return Response()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    code = main(
        [
            "review",
            str(page),
            "--api-key",
            "ar-test-key",
            "--base-url",
            "https://atmorouter.dev/v1/",
            "--model",
            "atmo/deepseek-v4.1-flash",
            "--timeout",
            "12",
        ]
    )
    assert code == 0
    assert captured["url"] == "https://atmorouter.dev/v1/chat/completions"
    assert captured["auth"] == "Bearer ar-test-key"
    assert captured["timeout"] == 12
    assert captured["body"]["model"] == "atmo/deepseek-v4.1-flash"
    user = captured["body"]["messages"][1]["content"]
    assert "hype-phrase" in user
    assert "ar-test-key" not in user
    assert "Replace the headline" in capsys.readouterr().out


def test_transport_error_is_a_distinct_exit(tmp_path, monkeypatch, capsys):
    page = tmp_path / "page.html"
    page.write_text("<p>Unlock the power of widgets</p>\n", encoding="utf-8")

    def fake_urlopen(_req, timeout=0):
        raise urllib.error.URLError("no route")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    code = main(["review", str(page), "--api-key", "ar-secret-value", "--base-url", "https://example.test/v1"])
    assert code == 3
    err = capsys.readouterr().err
    assert "review failed" in err
    assert "ar-secret-value" not in err
