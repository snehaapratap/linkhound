"""Check whether links are alive."""

import time
from dataclasses import dataclass

import requests

# Some servers don't support HEAD requests and answer with one of these codes.
HEAD_NOT_SUPPORTED = {405, 501}


@dataclass(frozen=True)
class LinkResult:
    url: str
    status: int | None
    elapsed_ms: float
    error: str | None = None

    @property
    def is_broken(self) -> bool:
        return self.error is not None or self.status is None or self.status >= 400


def check_link(url: str, session: requests.Session, timeout: float = 10.0) -> LinkResult:
    """Check a single URL.

    Uses a HEAD request first (fast, no body download) and falls back to GET
    when the server doesn't support HEAD.
    """
    start = time.perf_counter()
    try:
        response = session.head(url, allow_redirects=True, timeout=timeout)
        if response.status_code in HEAD_NOT_SUPPORTED:
            with session.get(url, allow_redirects=True, timeout=timeout, stream=True) as response:
                pass
    except requests.RequestException as exc:
        return LinkResult(url, None, _elapsed_ms(start), error=type(exc).__name__)

    return LinkResult(url, response.status_code, _elapsed_ms(start))


def _elapsed_ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000
