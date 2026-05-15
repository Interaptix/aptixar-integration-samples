"""Tests for AptixarClient.upload_file — end-to-end orchestration."""

import json

import pytest
import responses

from aptixar_uploader import AptixarClient, UploadResult


@pytest.fixture
def client():
    return AptixarClient("https://dev.aptixar.com", "aptx_int_test_token")


@responses.activate
def test_upload_file_runs_both_steps_and_returns_ids(client, tmp_path):
    sas_url = "https://blob.example/path/file.sog?sas=token"
    responses.add(
        responses.POST,
        "https://dev.aptixar.com/integrationgraphql/",
        json={"data": {"requestUpload": {
            "assetId": "asset-42",
            "jobId": "job-42",
            "expectedBlobUrl": "https://blob.example/path/file.sog",
            "sasUrl": sas_url,
        }}},
        status=200,
    )
    responses.add(responses.PUT, sas_url, status=201)

    file_path = tmp_path / "scene.sog"
    file_path.write_bytes(b"scene bytes")

    result = client.upload_file(str(file_path))

    assert isinstance(result, UploadResult)
    assert result.asset_id == "asset-42"
    assert result.job_id == "job-42"
    assert len(responses.calls) == 2


@responses.activate
def test_upload_file_derives_file_ext_from_path(client, tmp_path):
    responses.add(
        responses.POST,
        "https://dev.aptixar.com/integrationgraphql/",
        json={"data": {"requestUpload": {
            "assetId": "a", "jobId": "j", "expectedBlobUrl": "u",
            "sasUrl": "https://blob.example/file.lcc2?sas=t",
        }}},
        status=200,
    )
    responses.add(responses.PUT, "https://blob.example/file.lcc2?sas=t", status=201)

    file_path = tmp_path / "scan.lcc2"
    file_path.write_bytes(b"x")

    client.upload_file(str(file_path))

    body = json.loads(responses.calls[0].request.body)
    assert body["variables"]["fileExt"] == "lcc2"


@responses.activate
def test_upload_file_passes_name_and_folder(client, tmp_path):
    responses.add(
        responses.POST,
        "https://dev.aptixar.com/integrationgraphql/",
        json={"data": {"requestUpload": {
            "assetId": "a", "jobId": "j", "expectedBlobUrl": "u",
            "sasUrl": "https://blob.example/file.sog?sas=t",
        }}},
        status=200,
    )
    responses.add(responses.PUT, "https://blob.example/file.sog?sas=t", status=201)

    file_path = tmp_path / "x.sog"
    file_path.write_bytes(b"x")

    client.upload_file(str(file_path), name="My Scene", parent_folder_id="folder-9")

    body = json.loads(responses.calls[0].request.body)
    assert body["variables"]["name"] == "My Scene"
    assert body["variables"]["parentFolderId"] == "folder-9"


@responses.activate
def test_upload_file_defaults_name_and_folder_to_none(client, tmp_path):
    responses.add(
        responses.POST,
        "https://dev.aptixar.com/integrationgraphql/",
        json={"data": {"requestUpload": {
            "assetId": "a", "jobId": "j", "expectedBlobUrl": "u",
            "sasUrl": "https://blob.example/file.sog?sas=t",
        }}},
        status=200,
    )
    responses.add(responses.PUT, "https://blob.example/file.sog?sas=t", status=201)

    file_path = tmp_path / "x.sog"
    file_path.write_bytes(b"x")

    client.upload_file(str(file_path))

    body = json.loads(responses.calls[0].request.body)
    assert body["variables"]["name"] is None
    assert body["variables"]["parentFolderId"] is None


def test_upload_file_raises_if_file_has_no_extension(client, tmp_path):
    file_path = tmp_path / "noext"
    file_path.write_bytes(b"x")

    with pytest.raises(ValueError, match="extension"):
        client.upload_file(str(file_path))
