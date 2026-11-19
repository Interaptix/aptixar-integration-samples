"""Smoke test: confirms pytest + responses + the package import all work."""

import responses

from aptixar_uploader import AptixarClient


def test_client_constructs():
    client = AptixarClient("https://dev.aptixar.com", "aptx_int_test")
    assert client.base_url == "https://dev.aptixar.com"
    assert client.token == "aptx_int_test"


def test_client_strips_trailing_slash():
    client = AptixarClient("https://dev.aptixar.com/", "aptx_int_test")
    assert client.base_url == "https://dev.aptixar.com"


@responses.activate
def test_responses_library_is_available():
    responses.add(responses.GET, "https://example.com/", json={"ok": True}, status=200)
    import requests

    r = requests.get("https://example.com/")
    assert r.json() == {"ok": True}
