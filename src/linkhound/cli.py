"""Command-line entry point: ``linkhound <url>``."""

import argparse
import sys
from collections.abc import Sequence

import requests

from linkhound import __version__
from linkhound.checker import LinkResult, check_link
from linkhound.parser import extract_links

USER_AGENT = f"linkhound/{__version__} (+https://github.com/ivnpsvc/linkhound)"

# Exit codes let CI pipelines react to the result.
EXIT_OK = 0
EXIT_BROKEN_LINKS = 1
EXIT_FETCH_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="linkhound", description="Find broken links on a web page."
    )
    parser.add_argument("url", help="page to check, e.g. https://books.toscrape.com")
    parser.add_argument(
        "--timeout", type=float, default=10.0, help="seconds per request (default: 10)"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def format_result(result: LinkResult) -> str:
    mark = "BROKEN" if result.is_broken else "OK"
    status = result.error or str(result.status)
    return f"[{mark:>6}] {status:>4}  {result.elapsed_ms:7.0f} ms  {result.url}"


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    with requests.Session() as session:
        session.headers["User-Agent"] = USER_AGENT
        try:
            page = session.get(args.url, timeout=args.timeout)
            page.raise_for_status()
        except requests.RequestException as exc:
            print(f"error: could not fetch {args.url}: {exc}", file=sys.stderr)
            return EXIT_FETCH_ERROR

        links = extract_links(page.text, page.url)
        results = [check_link(link, session, args.timeout) for link in links]

    for result in results:
        print(format_result(result))

    broken = [r for r in results if r.is_broken]
    print(f"\nChecked {len(results)} links: {len(broken)} broken.")
    return EXIT_BROKEN_LINKS if broken else EXIT_OK
