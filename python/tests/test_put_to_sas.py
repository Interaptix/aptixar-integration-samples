"""Tests for AptixarClient._put_to_sas — the Azure Blob PUT call."""

import pytest
import responses

from aptixar_uploader import AptixarClient


@pytest.fixture
def client():
    return AptixarClient("https://dev.aptixar.com", "aptx_int_test_token")


@responses.activate
def test_put_to_sas_sends_body_and_blob_type(client, tmp_path):
    sas_url = "https://blob.example/path/file.sog?sas=token"
    responses.add(responses.PUT, sas_url, status=201)

    file_path = tmp_path / "scene.sog"
    file_path.write_bytes(b"binary scene data")

    client._put_to_sas(sas_url=sas_url, file_path=str(file_path))

    sent = responses.calls[0].request
    assert sent.body == b"binary scene data"
    assert sent.headers["x-ms-blob-type"] == "BlockBlob"


@responses.activate
def test_put_to_sas_does_not_send_auth_header(client, tmp_path):
    """SAS URL carries its own credential -- adding our Bearer would be wrong."""
    sas_url = "https://blob.example/path/file.sog?sas=token"
    responses.add(responses.PUT, sas_url, status=201)

    file_path = tmp_path / "scene.sog"
    file_path.write_bytes(b"x")

    client._put_to_sas(sas_url=sas_url, file_path=str(file_path))

    sent = responses.calls[0].request
    assert "Authorization" not in sent.headers


@responses.activate
def test_put_to_sas_raises_on_http_error(client, tmp_path):
    sas_url = "https://blob.example/path/file.sog?sas=token"
    responses.add(responses.PUT, sas_url, status=403, body="Forbidden")

    file_path = tmp_path / "scene.sog"
    file_path.write_bytes(b"x")

    with pytest.raises(RuntimeError, match="403"):
        client._put_to_sas(sas_url=sas_url, file_path=str(file_path))


def test_put_to_sas_raises_if_file_missing(client):
    with pytest.raises(FileNotFoundError):
        client._put_to_sas(sas_url="https://x/", file_path="/nonexistent/scene.sog")
