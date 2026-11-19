"""Reference Python client for the Aptixar Integration API."""

from aptixar_uploader.client import AptixarClient, UploadResult
from aptixar_uploader.names import MAX_ASSET_NAME_LENGTH, check_asset_name

__all__ = ["AptixarClient", "UploadResult", "check_asset_name", "MAX_ASSET_NAME_LENGTH"]
__version__ = "0.3.0"
