from collections.abc import Iterator

import pytest
import requests
import responses

from linkhound.checker import check_link

URL = "https://example.com/page"


@pytest.fixture
def session() -> Iterator[requests.Session]:
    with requests.Session() as s:
        yield s


@responses.activate
def test_working_link_is_not_broken(session: requests.Session) -> None:
    responses.head(URL, status=200)

    result = check_link(URL, session)

    assert result.status == 200
    assert not result.is_broken


@responses.activate
@pytest.mark.parametrize("status", [404, 410, 500, 503])
def test_error_status_is_broken(session: requests.Session, status: int) -> None:
    responses.head(URL, status=status)

    result = check_link(URL, session)

    assert result.status == status
    assert result.is_broken


@responses.activate
def test_falls_back_to_get_when_head_not_allowed(session: requests.Session) -> None:
    responses.head(URL, status=405)
    responses.get(URL, status=200)

    result = check_link(URL, session)

    assert result.status == 200
    assert not result.is_broken


@responses.activate
def test_follows_redirects(session: requests.Session) -> None:
    responses.head(URL, status=301, headers={"Location": "https://example.com/new"})
    responses.head("https://example.com/new", status=200)

    result = check_link(URL, session)

    assert result.status == 200


@responses.activate
def test_connection_error_is_broken(session: requests.Session) -> None:
    responses.head(URL, body=requests.ConnectionError("connection refused"))

    result = check_link(URL, session)

    assert result.status is None
    assert result.error == "ConnectionError"
    assert result.is_broken
