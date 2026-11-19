"""Tests for check_asset_name and the name check in upload_file."""

import json

import pytest
import responses

from aptixar_uploader import MAX_ASSET_NAME_LENGTH, AptixarClient, check_asset_name


@pytest.mark.parametrize("name", [
    "Site A scan 01",
    "厂房扫描 一号楼",
    "Scan (v2) [final] {x}",
    "scan-2026-11-19",
    "scan_area_03",
    "Café #1 & 2 @ 50% ; 'ok' ~ !",
    "📦 box scan",
    "",
])
def test_accepted_names_are_unchanged(name):
    assert check_asset_name(name) == name


def test_reserved_characters_become_hyphens():
    assert check_asset_name('a<b>c"d\\e/f|g?h*i') == "a-b-c-d-e-f-g-h-i"


@pytest.mark.parametrize("name", ["x" * 64, "扫" * 64, "é" * 64])
def test_limit_is_64_characters_not_bytes(name):
    assert MAX_ASSET_NAME_LENGTH == 64
    assert check_asset_name(name) == name


@pytest.mark.parametrize("name", ["x" * 65, "扫" * 65])
def test_over_64_characters_is_rejected(name):
    with pytest.raises(ValueError, match="65 characters; the limit is 64"):
        check_asset_name(name)


@pytest.fixture
def client():
    return AptixarClient("https://dev.aptixar.com", "aptx_int_test_token")


@responses.activate
def test_upload_file_rejects_long_name_before_any_request(client, tmp_path):
    file_path = tmp_path / "scene.sog"
    file_path.write_bytes(b"x")

    with pytest.raises(ValueError, match="limit is 64"):
        client.upload_file(str(file_path), name="x" * 65)

    assert len(responses.calls) == 0


@responses.activate
def test_upload_file_sends_the_name_the_portal_will_show(client, tmp_path):
    sas_url = "https://blob.example/file.sog?sas=t"
    responses.add(
        responses.POST,
        "https://dev.aptixar.com/integrationgraphql/",
        json={"data": {"requestUpload": {
            "assetId": "a", "jobId": "j", "expectedBlobUrl": "u", "sasUrl": sas_url,
        }}},
        status=200,
    )
    responses.add(responses.PUT, sas_url, status=201)
    file_path = tmp_path / "scene.sog"
    file_path.write_bytes(b"x")

    client.upload_file(str(file_path), name="Line 3 / Station 7?")

    body = json.loads(responses.calls[0].request.body)
    assert body["variables"]["name"] == "Line 3 - Station 7-"
