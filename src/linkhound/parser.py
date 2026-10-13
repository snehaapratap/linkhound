"""Extract links from HTML."""

from urllib.parse import urldefrag, urljoin

from bs4 import BeautifulSoup

# Links with these schemes can't be checked over HTTP, so we skip them.
SKIPPED_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")


def extract_links(html: str, base_url: str) -> list[str]:
    """Return unique absolute URLs from all <a href> tags, in page order.

    Relative links are resolved against ``base_url`` and #fragments are dropped,
    because ``/docs#intro`` and ``/docs#usage`` point to the same page.
    """
    soup = BeautifulSoup(html, "html.parser")
    links: dict[str, None] = {}  # a dict keeps insertion order and removes duplicates

    for tag in soup.select("a[href]"):
        href = tag.get("href")
        if not isinstance(href, str):
            continue
        href = href.strip()
        if not href or href.startswith("#") or href.lower().startswith(SKIPPED_SCHEMES):
            continue
        absolute_url, _fragment = urldefrag(urljoin(base_url, href))
        links[absolute_url] = None

    return list(links)
