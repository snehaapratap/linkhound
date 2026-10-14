# 🐕 linkhound

[![CI](https://github.com/ivnpsvc/linkhound/actions/workflows/ci.yml/badge.svg)](https://github.com/ivnpsvc/linkhound/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A command-line tool that sniffs out broken links on web pages. It's built to run in CI: the
exit code tells your pipeline whether the site is healthy.

```console
$ linkhound https://the-internet.herokuapp.com/status_codes
[    OK]  200      123 ms  https://the-internet.herokuapp.com/status_codes/200
[BROKEN]  404      119 ms  https://the-internet.herokuapp.com/status_codes/404
[BROKEN]  500      121 ms  https://the-internet.herokuapp.com/status_codes/500

Checked 7 links: 2 broken.
```

## Features

- [x] Finds all links on a page, resolves relative URLs, removes duplicates
- [x] Fast checks with `HEAD`, falling back to `GET` for servers that don't support it
- [x] Follows redirects, reports response time per link
- [x] Flags redirects without a usable destination (`MissingRedirectLocation`)
- [x] CI-friendly exit codes
- [ ] Crawl a whole site (same domain, configurable depth)
- [ ] Respect `robots.txt` and rate limits
- [ ] Concurrent checking
- [ ] Flag slow pages and images missing `alt` text
- [ ] JSON / JUnit XML output for CI reports
- [ ] Published to PyPI

## Usage

```bash
uv run linkhound https://books.toscrape.com
uv run linkhound https://example.com --timeout 5
```

| Exit code | Meaning |
|---|---|
| `0` | All links work |
| `1` | At least one broken link |
| `2` | The page itself could not be fetched |

## Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
make install   # dependencies + git pre-commit hooks
make check     # lint, format check, type check, tests (same as CI)
```

| Tool | Purpose |
|---|---|
| **pytest** + **responses** | Unit tests with mocked HTTP: fast, no network needed |
| **pytest-cov** | Coverage, CI fails below 90% |
| **ruff** | Linting and formatting |
| **mypy** (strict) | Static type checking |
| **pre-commit** | Runs the checks before every commit |
| **GitHub Actions** | CI on every push and pull request, Python 3.12 + 3.13 |

## Testing approach

Unit tests mock HTTP with `responses`, so the suite runs in under a second and never
depends on an external site being up. Each behaviour (status codes, `HEAD` → `GET` fallback,
redirects, connection errors, exit codes) has its own focused test.
