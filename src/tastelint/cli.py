"""Command line for tastelint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tastelint import __version__
from tastelint.engine import scan_path
from tastelint.formatters import render
from tastelint.review import review_path
from tastelint.rules import RULES
from tastelint.score import FORMULA
from tastelint.skill import TARGETS, display, install


def _gate(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("fail-under must be an integer") from exc
    if number < 0 or number > 100:
        raise argparse.ArgumentTypeError("fail-under must be between 0 and 100")
    return number


def _write(text: str, output: str | None) -> None:
    sys.stdout.write(text)
    if not text.endswith("\n"):
        sys.stdout.write("\n")
    if output:
        Path(output).write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def _cmd_scan(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.exists():
        print(f"path not found: {args.path}", file=sys.stderr)
        return 2
    report = scan_path(path, fail_under=args.fail_under, target=args.path)
    text = render(report, args.format, verbose=args.verbose, quiet=args.quiet)
    _write(text, args.output)
    return 0 if report.passed else 1


def _cmd_review(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.exists():
        print(f"path not found: {args.path}", file=sys.stderr)
        return 2
    code, text = review_path(
        path,
        base_url=args.base_url,
        model=args.model,
        api_key=args.api_key,
        timeout=args.timeout,
        dry_run=args.dry_run,
        fail_under=args.fail_under,
        target=args.path,
    )
    stream = sys.stdout if code in {0, 1} else sys.stderr
    stream.write(text)
    if not text.endswith("\n"):
        stream.write("\n")
    return code


def _cmd_skill(args: argparse.Namespace) -> int:
    dest = Path(args.dest)
    written = install(args.target, dest)
    print(f"installed {display(written, dest)}")
    return 0


def _cmd_rules(_args: argparse.Namespace) -> int:
    print(FORMULA)
    print()
    for spec in RULES:
        print(f"{spec.id:<18} {spec.severity:<8} {spec.summary}")
        print(f"{'':<18} {'':<8} {spec.hint}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tastelint",
        description="Taste linter for generated UI. Flags the patterns coding agents repeat.",
    )
    parser.add_argument("--version", action="version", version=f"tastelint {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan UI source and print a taste score")
    scan.add_argument("path", help="File or directory")
    scan.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    scan.add_argument("--fail-under", type=_gate, default=None, help="Exit 1 when the score is below N")
    scan.add_argument("--verbose", action="store_true", help="Include hints and source lines")
    scan.add_argument("--quiet", action="store_true", help="Print only the summary")
    scan.add_argument("-o", "--output", help="Also write the report to this file")
    scan.set_defaults(func=_cmd_scan)

    review = sub.add_parser("review", help="Ask an OpenAI-compatible model for concrete edits")
    review.add_argument("path", help="File or directory")
    review.add_argument("--base-url", help="Chat completions root, default https://atmorouter.dev/v1")
    review.add_argument("--model", help="Model id, default atmo/deepseek-v4.1-flash")
    review.add_argument("--api-key", help="Bearer key. Prefer ATMOROUTER_API_KEY")
    review.add_argument("--timeout", type=float, default=60)
    review.add_argument("--dry-run", action="store_true", help="Print the prompt and do not call the network")
    review.add_argument("--fail-under", type=_gate, default=None)
    review.set_defaults(func=_cmd_review)

    skill = sub.add_parser("skill", help="Install agent guidance")
    skill_sub = skill.add_subparsers(dest="skill_command", required=True)
    inst = skill_sub.add_parser("install", help="Write a skill or rules file")
    inst.add_argument("--target", required=True, choices=TARGETS)
    inst.add_argument("--dest", default=".", help="Project root to write into")
    inst.set_defaults(func=_cmd_skill)

    rules = sub.add_parser("rules", help="List the rules and what to do about them")
    rules.set_defaults(func=_cmd_rules)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
