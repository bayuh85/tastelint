"""Find UI source files. Hidden directories and dependencies are skipped."""

from __future__ import annotations

import os
from pathlib import Path

EXTENSIONS = {
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".jsx",
    ".tsx",
    ".vue",
    ".svelte",
    ".js",
    ".ts",
    ".mdx",
}

SKIP_DIRS = {
    "node_modules",
    "dist",
    "build",
    ".next",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "coverage",
    "artifacts",
    "site-packages",
}

MAX_BYTES = 1_500_000


def is_ui_file(path: Path) -> bool:
    name = path.name.lower()
    if name.startswith("."):
        return False
    if name.endswith(".min.js") or name.endswith(".min.css"):
        return False
    return path.suffix.lower() in EXTENSIONS


def discover(path: Path) -> list[Path]:
    path = path.resolve()
    if path.is_file():
        return [path] if is_ui_file(path) else []
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = sorted(
            name
            for name in dirnames
            if not name.startswith(".") and name not in SKIP_DIRS
        )
        for name in sorted(filenames):
            candidate = Path(dirpath) / name
            if not is_ui_file(candidate):
                continue
            try:
                size = candidate.stat().st_size
            except OSError:
                continue
            if size <= MAX_BYTES:
                found.append(candidate)
    return found


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()
