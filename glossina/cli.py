"""Command-line interface for glossina."""

import argparse
import json
import sys
from pathlib import Path

from glossina.matcher import rank_matches
from glossina.spdx_client import download_spdx_corpus


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="glossina",
        description="Compare pasted text against the SPDX License List.",
    )

    parser.add_argument("-t", "--text", help="Text input to compare directly")
    parser.add_argument("-f", "--file", help="Read text input from a file")
    parser.add_argument("--top", type=int, default=10, help="Number of matches to return (default: 10)")
    parser.add_argument(
        "--min-score",
        type=float,
        default=25.0,
        help="Minimum score threshold 0-100 (default: 25)",
    )
    parser.add_argument("--no-exceptions", action="store_true", help="Skip SPDX exceptions")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if args.top < 1:
        parser.error("--top must be a positive number")
    if not 0 <= args.min_score <= 100:
        parser.error("--min-score must be between 0 and 100")

    return args


def resolve_input(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if sys.stdin.isatty():
        raise ValueError("No input detected. Pipe text to stdin, or use --text/--file.")
    return sys.stdin.read()


def print_table(matches: list[dict]) -> None:
    if not matches:
        print("No matches found for the configured threshold.")
        return

    for index, match in enumerate(matches, start=1):
        print(f"{index}. {match['id']} ({match['category']})")
        print(f"   Name: {match['name']}")
        print(
            "   Score: "
            f"{match['score']:.2f} | "
            f"Dice: {match['dice']:.2f} | "
            f"Levenshtein: {match['lev_percent']:.2f}"
        )
        print(f"   Reference: {match['reference']}")


def main() -> int:
    try:
        args = parse_args()
        input_text = resolve_input(args)

        corpus = download_spdx_corpus(include_exceptions=not args.no_exceptions)
        matches = rank_matches(
            input_text,
            corpus,
            top=args.top,
            min_score=args.min_score,
        )

        if args.json:
            print(json.dumps(matches, indent=2))
        else:
            print_table(matches)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
