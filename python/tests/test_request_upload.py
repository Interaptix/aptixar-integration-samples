"""Tests for AptixarClient._request_upload — the GraphQL mutation call."""

import json

import pytest
import responses

from aptixar_uploader import AptixarClient


@pytest.fixture
def client():
    return AptixarClient("https://dev.aptixar.com", "aptx_int_test_token")


@responses.activate
def test_request_upload_posts_to_correct_url(client):
    responses.add(
        responses.POST,
        "https://dev.aptixar.com/integrationgraphql/",
        json={"data": {"requestUpload": {
            "assetId": "asset-1",
            "jobId": "job-1",
            "expectedBlobUrl": "https://blob.example/path",
            "sasUrl": "https://blob.example/path?sas=token",
        }}},
        status=200,
    )

    result = client._request_upload(file_ext="sog", name="scene1", parent_folder_id=None)

    assert result["assetId"] == "asset-1"
    assert result["jobId"] == "job-1"
    assert result["sasUrl"] == "https://blob.example/path?sas=token"


@responses.activate
def test_request_upload_sends_bearer_header(client):
    responses.add(
        responses.POST,
        "https://dev.aptixar.com/integrationgraphql/",
        json={"data": {"requestUpload": {
            "assetId": "a", "jobId": "j", "expectedBlobUrl": "u", "sasUrl": "s",
        }}},
        status=200,
    )

    client._request_upload(file_ext="sog", name=None, parent_folder_id=None)

    sent = responses.calls[0].request
    assert sent.headers["Authorization"] == "Bearer aptx_int_test_token"
    assert sent.headers["Content-Type"] == "application/json"


@responses.activate
def test_request_upload_sends_variables(client):
    responses.add(
        responses.POST,
        "https://dev.aptixar.com/integrationgraphql/",
        json={"data": {"requestUpload": {
            "assetId": "a", "jobId": "j", "expectedBlobUrl": "u", "sasUrl": "s",
        }}},
        status=200,
    )

    client._request_upload(file_ext="sog", name="scene1", parent_folder_id="folder-1")

    body = json.loads(responses.calls[0].request.body)
    assert body["variables"] == {
        "fileExt": "sog",
        "name": "scene1",
        "parentFolderId": "folder-1",
    }
    assert "requestUpload" in body["query"]


@responses.activate
def test_request_upload_raises_on_graphql_error(client):
    responses.add(
        responses.POST,
        "https://dev.aptixar.com/integrationgraphql/",
        json={"errors": [{"message": "Forbidden"}]},
        status=200,
    )

    with pytest.raises(RuntimeError, match="Forbidden"):
        client._request_upload(file_ext="sog", name=None, parent_folder_id=None)


@responses.activate
def test_request_upload_raises_on_http_error(client):
    responses.add(
        responses.POST,
        "https://dev.aptixar.com/integrationgraphql/",
        json={"detail": "Unauthorized"},
        status=401,
    )

    with pytest.raises(RuntimeError, match="401"):
        client._request_upload(file_ext="sog", name=None, parent_folder_id=None)
