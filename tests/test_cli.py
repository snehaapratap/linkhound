import pytest
import responses

from linkhound.cli import EXIT_BROKEN_LINKS, EXIT_FETCH_ERROR, EXIT_OK, main

PAGE_URL = "https://example.com/"


@responses.activate
def test_exits_ok_when_all_links_work(capsys: pytest.CaptureFixture[str]) -> None:
    responses.get(PAGE_URL, body='<a href="/ok">ok</a>')
    responses.head("https://example.com/ok", status=200)

    exit_code = main([PAGE_URL])

    assert exit_code == EXIT_OK
    assert "Checked 1 links: 0 broken." in capsys.readouterr().out


@responses.activate
def test_reports_broken_links(capsys: pytest.CaptureFixture[str]) -> None:
    responses.get(PAGE_URL, body='<a href="/ok">ok</a><a href="/missing">gone</a>')
    responses.head("https://example.com/ok", status=200)
    responses.head("https://example.com/missing", status=404)

    exit_code = main([PAGE_URL])

    out = capsys.readouterr().out
    assert exit_code == EXIT_BROKEN_LINKS
    assert "BROKEN" in out
    assert "https://example.com/missing" in out
    assert "Checked 2 links: 1 broken." in out


@responses.activate
def test_fails_when_page_cannot_be_fetched(capsys: pytest.CaptureFixture[str]) -> None:
    responses.get(PAGE_URL, status=500)

    exit_code = main([PAGE_URL])

    assert exit_code == EXIT_FETCH_ERROR
    assert "could not fetch" in capsys.readouterr().err


@responses.activate
def test_sends_identifying_user_agent() -> None:
    responses.get(PAGE_URL, body="<p>no links</p>")

    main([PAGE_URL])

    assert responses.calls[0].request.headers["User-Agent"].startswith("linkhound/")
