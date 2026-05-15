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

    def _put_to_sas(self, sas_url: str, file_path: str) -> None:
        """PUT file bytes to the Azure Blob SAS URL.

        The SAS URL carries its own credential; we MUST NOT add our Bearer header.
        Azure requires `x-ms-blob-type: BlockBlob` on PUT.
        """
        with open(file_path, "rb") as f:
            response = requests.put(
                sas_url,
                data=f,
                headers={"x-ms-blob-type": "BlockBlob"},
                timeout=600,
            )

        if response.status_code not in (200, 201):
            raise RuntimeError(
                f"SAS upload HTTP {response.status_code}: {response.text[:200]}"
            )

    def upload_file(
        self,
        file_path: str,
        name: Optional[str] = None,
        parent_folder_id: Optional[str] = None,
    ) -> UploadResult:
        """Upload a file end-to-end. Returns asset_id and job_id."""
        import os

        ext = os.path.splitext(file_path)[1].lstrip(".")
        if not ext:
            raise ValueError(
                f"Cannot derive fileExt from path with no extension: {file_path}"
            )

        payload = self._request_upload(
            file_ext=ext,
            name=name,
            parent_folder_id=parent_folder_id,
        )
        self._put_to_sas(sas_url=payload["sasUrl"], file_path=file_path)

        return UploadResult(
            asset_id=str(payload["assetId"]),
            job_id=str(payload["jobId"]),
        )
