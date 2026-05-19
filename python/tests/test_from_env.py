"""Tests for AptixarClient.from_env — reads APTIXAR_* env vars."""

import pytest

from aptixar_uploader import AptixarClient

_BASE_URL = "https://api.aptixar.com"


def test_from_env_reads_base_url_and_token(monkeypatch):
    monkeypatch.setenv("APTIXAR_BASE_URL", _BASE_URL)
    monkeypatch.setenv("APTIXAR_TOKEN", "aptx_int_abc123")

    client = AptixarClient.from_env()

    assert client.base_url == _BASE_URL
    assert client.token == "aptx_int_abc123"


def test_from_env_defaults_base_url_when_unset(monkeypatch):
    monkeypatch.delenv("APTIXAR_BASE_URL", raising=False)
    monkeypatch.setenv("APTIXAR_TOKEN", "aptx_int_abc123")

    client = AptixarClient.from_env()

    assert client.base_url == _BASE_URL


def test_from_env_raises_clearly_when_token_missing(monkeypatch):
    monkeypatch.setenv("APTIXAR_BASE_URL", _BASE_URL)
    monkeypatch.delenv("APTIXAR_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="APTIXAR_TOKEN"):
        AptixarClient.from_env()
