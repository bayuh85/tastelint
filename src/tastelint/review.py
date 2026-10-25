"""Send a compact taste report to an OpenAI-compatible chat endpoint.

The default host is AtmoRouter. Any other host that speaks chat completions
works if you pass --base-url, --model, and a key.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from tastelint import __version__
from tastelint.charter import review_system_prompt
from tastelint.engine import scan_path
from tastelint.model import Report

DEFAULT_BASE_URL = "https://atmorouter.dev/v1"
DEFAULT_MODEL = "atmo/deepseek-v4.1-flash"
FINDING_LIMIT = 20


def load_env_file(path: Path) -> None:
    """Fill missing environment variables from a local .env file."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def resolve_settings(base_url: str | None, model: str | None, api_key: str | None) -> tuple[str, str, str | None]:
    load_env_file(Path.cwd() / ".env")
    base = base_url or os.environ.get("TASTELINT_BASE_URL") or os.environ.get("ATMOROUTER_BASE_URL") or DEFAULT_BASE_URL
    chosen = model or os.environ.get("TASTELINT_MODEL") or DEFAULT_MODEL
    key = api_key or os.environ.get("TASTELINT_API_KEY") or os.environ.get("ATMOROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    return base.rstrip("/"), chosen, key


def endpoint_for(base_url: str) -> str:
    root = base_url.rstrip("/")
    if root.endswith("/chat/completions"):
        return root
    return root + "/chat/completions"


def compact_report(report: Report, limit: int = FINDING_LIMIT) -> dict:
    rows = []
    for finding in report.findings[:limit]:
        rows.append(
            {
                "rule": finding.rule_id,
                "severity": finding.severity,
                "path": finding.path,
                "line": finding.line,
                "message": finding.message,
                "hint": finding.hint,
                "snippet": finding.snippet[:160],
            }
        )
    return {
        "taste_score": report.score,
        "files": report.file_count,
        "finding_count": len(report.findings),
        "shown": len(rows),
        "findings": rows,
    }


def user_message(report: Report) -> str:
    payload = json.dumps(compact_report(report), indent=2, ensure_ascii=False)
    return (
        "Critique this interface using the Plain Surface Charter. "
        "Return concrete edits only.\n\n"
        + payload
    )


def _message_text(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
        return "\n".join(part for part in parts if part).strip()
    return ""


def request_review(base_url: str, model: str, api_key: str, report: Report, timeout: float) -> str:
    body = {
        "model": model,
        "temperature": 0.2,
        "max_tokens": 700,
        "messages": [
            {"role": "system", "content": review_system_prompt()},
            {"role": "user", "content": user_message(report)},
        ],
    }
    req = urllib.request.Request(
        endpoint_for(base_url),
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"tastelint/{__version__}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:600]
        raise RuntimeError(f"HTTP {exc.code}\n{detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc.reason)) from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("response was not JSON") from exc
    if isinstance(payload, dict) and payload.get("error") and not payload.get("choices"):
        error = payload["error"]
        message = error.get("message") if isinstance(error, dict) else str(error)
        raise RuntimeError(message or "request rejected")
    choices = payload.get("choices") if isinstance(payload, dict) else None
    if not choices:
        raise RuntimeError("response had no choices")
    message = choices[0].get("message") or {}
    text = _message_text(message.get("content"))
    if not text:
        raise RuntimeError("response message was empty")
    return text


def review_path(
    path: Path,
    *,
    base_url: str | None,
    model: str | None,
    api_key: str | None,
    timeout: float,
    dry_run: bool,
    fail_under: int | None,
    target: str | None = None,
) -> tuple[int, str]:
    report = scan_path(path, fail_under=fail_under, target=target)
    if not report.findings:
        text = f"Nothing to review. Taste score is {report.score}/100.\n"
        return (0 if report.passed else 1), text
    base, chosen, key = resolve_settings(base_url, model, api_key)
    if dry_run:
        rendered = (
            f"dry run  ·  {endpoint_for(base)}  ·  model {chosen}  ·  "
            f"taste score {report.score}/100\n"
            "network was not called\n\n"
            + user_message(report)
            + "\n"
        )
        return (0 if report.passed else 1), rendered
    if not key:
        message = (
            "Set ATMOROUTER_API_KEY, or pass --api-key.\n"
            f"Default endpoint is {DEFAULT_BASE_URL} and the default model is {DEFAULT_MODEL}.\n"
        )
        return 4, message
    try:
        critique = request_review(base, chosen, key, report, timeout)
    except RuntimeError as exc:
        return 3, f"review failed: {exc}\n"
    rendered = (
        f"tastelint review  ·  model {chosen}  ·  taste score {report.score}/100\n\n"
        + critique
        + "\n"
    )
    return (0 if report.passed else 1), rendered
