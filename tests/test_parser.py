import pytest

from linkhound.parser import extract_links

BASE_URL = "https://example.com/blog/"


@pytest.mark.parametrize(
    ("href", "expected"),
    [
        pytest.param("https://other.com/page", "https://other.com/page", id="absolute"),
        pytest.param("post-1", "https://example.com/blog/post-1", id="relative"),
        pytest.param("/about", "https://example.com/about", id="root-relative"),
        pytest.param("../contact", "https://example.com/contact", id="parent-relative"),
        pytest.param("/docs#usage", "https://example.com/docs", id="fragment-dropped"),
        pytest.param("  /spaces  ", "https://example.com/spaces", id="whitespace-trimmed"),
    ],
)
def test_resolves_link_to_absolute_url(href: str, expected: str) -> None:
    html = f'<a href="{href}">link</a>'

    assert extract_links(html, BASE_URL) == [expected]


@pytest.mark.parametrize(
    "href",
    ["mailto:hi@example.com", "tel:+385123456", "javascript:void(0)", "#top", ""],
)
def test_skips_links_that_cannot_be_checked(href: str) -> None:
    html = f'<a href="{href}">link</a>'

    assert extract_links(html, BASE_URL) == []


def test_removes_duplicates_and_keeps_page_order() -> None:
    html = """
        <a href="/b">B</a>
        <a href="/a">A</a>
        <a href="/b#again">B again</a>
    """

    assert extract_links(html, BASE_URL) == [
        "https://example.com/b",
        "https://example.com/a",
    ]


def test_ignores_anchors_without_href() -> None:
    html = '<a name="section">no href</a><a href="/real">real</a>'

    assert extract_links(html, BASE_URL) == ["https://example.com/real"]
