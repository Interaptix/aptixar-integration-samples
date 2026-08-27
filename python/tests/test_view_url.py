"""Tests for AptixarClient.view_url — the web portal link built from an assetId."""

import pytest

from aptixar_uploader import AptixarClient

_ASSET_ID = "1a2b3c4d-0000-0000-0000-000000000001"


@pytest.fixture
def client():
    return AptixarClient("https://api.aptixar.com", "aptx_int_test_token")


def test_view_url_defaults_to_the_prod_portal(client):
    assert client.view_url(_ASSET_ID) == f"https://www.aptixar.com/assets?assetId={_ASSET_ID}"


def test_view_url_is_not_derived_from_the_api_host():
    """The portal and the API are different hosts -- one must not be inferred from the other."""
    client = AptixarClient("https://api.aptixar.com", "aptx_int_test_token")

    assert "api.aptixar.com" not in client.view_url(_ASSET_ID)


def test_view_url_honours_an_explicit_portal_url():
    client = AptixarClient(
        "https://dev-api.aptixar.com",
        "aptx_int_test_token",
        portal_url="https://dev.aptixar.com",
    )

    assert client.view_url(_ASSET_ID) == f"https://dev.aptixar.com/assets?assetId={_ASSET_ID}"


def test_view_url_strips_trailing_slash_from_portal_url():
    client = AptixarClient(
        "https://api.aptixar.com",
        "aptx_int_test_token",
        portal_url="https://dev.aptixar.com/",
    )

    assert client.view_url(_ASSET_ID) == f"https://dev.aptixar.com/assets?assetId={_ASSET_ID}"
