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
    #: Web portal link that opens the uploaded scene. Valid immediately -- see
    #: `AptixarClient.view_url`.
    view_url: str


class AptixarClient:
    """Reference client for the Aptixar Integration API.

    Two-step upload protocol:
      1. POST GraphQL `requestUpload` mutation -> server returns a SAS URL.
      2. PUT file bytes to the SAS URL (Azure Blob).
    """

    #: Integration API. Where `requestUpload` is POSTed.
    _DEFAULT_BASE_URL = "https://api.aptixar.com"
    #: Web portal. A different host from the API -- view links are built here.
    _DEFAULT_PORTAL_URL = "https://www.aptixar.com"

    def __init__(self, base_url: str, token: str, portal_url: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.portal_url = (portal_url or self._DEFAULT_PORTAL_URL).rstrip("/")

    def view_url(self, asset_id: str) -> str:
        """Web portal link that opens the scene for `asset_id`.

        Buildable the moment `requestUpload` returns: it keys off the asset, not
        the processed scene, so there is nothing to wait for and nothing to poll.
        Opened before processing finishes, the page reports progress and switches
        itself to the scene once one exists.
        """
        return f"{self.portal_url}/assets?assetId={asset_id}"

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
        """Upload a file end-to-end. Returns the ids and a portal view link."""
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

        asset_id = str(payload["assetId"])
        return UploadResult(
            asset_id=asset_id,
            job_id=str(payload["jobId"]),
            view_url=self.view_url(asset_id),
        )

    @classmethod
    def from_env(cls) -> "AptixarClient":
        """Construct from APTIXAR_BASE_URL, APTIXAR_PORTAL_URL and APTIXAR_TOKEN env vars.

        Loads .env in the current working directory via python-dotenv if present.
        Defaults APTIXAR_BASE_URL to the prod Aptixar integration API and
        APTIXAR_PORTAL_URL to the prod web portal.
        Raises RuntimeError if APTIXAR_TOKEN is unset.
        """
        import os

        from dotenv import load_dotenv

        load_dotenv()
        base_url = os.environ.get("APTIXAR_BASE_URL", cls._DEFAULT_BASE_URL)
        portal_url = os.environ.get("APTIXAR_PORTAL_URL", cls._DEFAULT_PORTAL_URL)
        token = os.environ.get("APTIXAR_TOKEN")
        if not token:
            raise RuntimeError(
                "APTIXAR_TOKEN is not set. Copy .env.template to .env and fill it in."
            )
        return cls(base_url=base_url, token=token, portal_url=portal_url)
