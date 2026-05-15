"""Tests for the aptixar_uploader.cli module."""

import sys
from unittest.mock import patch

import pytest

from aptixar_uploader import UploadResult
from aptixar_uploader.cli import main


def test_cli_upload_prints_asset_and_job_ids(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("APTIXAR_BASE_URL", "https://dev.aptixar.com")
    monkeypatch.setenv("APTIXAR_TOKEN", "aptx_int_test")

    file_path = tmp_path / "x.sog"
    file_path.write_bytes(b"x")

    fake_result = UploadResult(asset_id="asset-1", job_id="job-1")

    with patch("aptixar_uploader.cli.AptixarClient") as MockClient:
        MockClient.from_env.return_value.upload_file.return_value = fake_result
        monkeypatch.setattr(sys, "argv", ["aptixar-upload", "upload", str(file_path)])
        main()

    captured = capsys.readouterr()
    assert "asset-1" in captured.out
    assert "job-1" in captured.out


def test_cli_upload_passes_name_and_folder(monkeypatch, tmp_path):
    monkeypatch.setenv("APTIXAR_BASE_URL", "https://dev.aptixar.com")
    monkeypatch.setenv("APTIXAR_TOKEN", "aptx_int_test")

    file_path = tmp_path / "x.sog"
    file_path.write_bytes(b"x")

    fake_result = UploadResult(asset_id="a", job_id="j")

    with patch("aptixar_uploader.cli.AptixarClient") as MockClient:
        instance = MockClient.from_env.return_value
        instance.upload_file.return_value = fake_result
        monkeypatch.setattr(
            sys,
            "argv",
            ["aptixar-upload", "upload", str(file_path), "--name", "My Scene", "--folder", "folder-9"],
        )
        main()

        instance.upload_file.assert_called_once_with(
            str(file_path),
            name="My Scene",
            parent_folder_id="folder-9",
        )


def test_cli_upload_exits_nonzero_on_runtime_error(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("APTIXAR_BASE_URL", "https://dev.aptixar.com")
    monkeypatch.setenv("APTIXAR_TOKEN", "aptx_int_test")

    file_path = tmp_path / "x.sog"
    file_path.write_bytes(b"x")

    with patch("aptixar_uploader.cli.AptixarClient") as MockClient:
        MockClient.from_env.return_value.upload_file.side_effect = RuntimeError("nope")
        monkeypatch.setattr(sys, "argv", ["aptixar-upload", "upload", str(file_path)])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        err = capsys.readouterr().err
        assert "nope" in err
