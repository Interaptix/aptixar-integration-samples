"""Aptixar Integration API client. Two-step upload: GraphQL request_upload, then PUT to SAS URL."""

from dataclasses import dataclass


@dataclass
class UploadResult:
    asset_id: str
    job_id: str


class AptixarClient:
    """Placeholder. Implemented in Tasks 4-7."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
