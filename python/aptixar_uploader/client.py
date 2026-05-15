"""Aptixar Integration API client. Two-step upload: GraphQL request_upload, then PUT to SAS URL."""

from dataclasses import dataclass
from typing import Optional

import requests

_REQUEST_UPLOAD_MUTATION = """
mutation RequestUpload($fileExt: String!, $name: String, $parentFolderId: ID) {
  requestUpload(fileExt: $fileExt, name: $name, parentFolderId: $parentFolderId)
}
""".strip()


@dataclass
class UploadResult:
    asset_id: str
    job_id: str


class AptixarClient:
    """Reference client for the Aptixar Integration API.

    Two-step upload protocol:
      1. POST GraphQL `requestUpload` mutation -> server returns a SAS URL.
      2. PUT file bytes to the SAS URL (Azure Blob).
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _request_upload(
        self,
        file_ext: str,
        name: Optional[str],
        parent_folder_id: Optional[str],
    ) -> dict:
        """POST the requestUpload GraphQL mutation. Returns the server's payload dict."""
        url = f"{self.base_url}/integrationgraphql/"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "query": _REQUEST_UPLOAD_MUTATION,
            "variables": {
                "fileExt": file_ext,
                "name": name,
                "parentFolderId": parent_folder_id,
            },
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(
                f"requestUpload HTTP {response.status_code}: {response.text}"
            )

        body = response.json()
        if "errors" in body and body["errors"]:
            messages = "; ".join(e.get("message", "unknown") for e in body["errors"])
            raise RuntimeError(f"requestUpload GraphQL error: {messages}")

        return body["data"]["requestUpload"]
