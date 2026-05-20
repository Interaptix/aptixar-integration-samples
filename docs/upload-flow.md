# Upload flow

This is the canonical protocol document. The Python reference in `../python/` implements exactly this flow; partners on other stacks can read this file and port the protocol directly.

## Overview

Uploading a file to Aptixar takes three steps:

1. **Admin creates an integration token** — see [authentication.md](authentication.md).
2. **Partner calls `requestUpload`** — a GraphQL mutation that returns a temporary Azure Blob SAS URL.
3. **Partner `PUT`s the file** to that SAS URL.

The server creates the asset record during Step 1 (you get back its `assetId` immediately). Once the PUT completes in Step 2, the server's IMPORT processor takes over and attaches a snapshot — previews, mesh files, etc. — to that asset.

---

## Step 1: `requestUpload` mutation

**Endpoint:** `POST {APTIXAR_BASE_URL}/integrationgraphql/`

**Required headers:**

| Header | Value |
|---|---|
| `Authorization` | `Bearer aptx_int_<your-token>` |
| `Content-Type` | `application/json` |

**Request body:**

```json
{
  "query": "mutation RequestUpload($fileExt: String!, $name: String, $parentFolderId: ID) { requestUpload(fileExt: $fileExt, name: $name, parentFolderId: $parentFolderId) }",
  "variables": {
    "fileExt": "sog",
    "name": "Scene name (optional)",
    "parentFolderId": null
  }
}
```

Variables:

- `fileExt` (required) — file extension without leading dot. See [file-types.md](file-types.md).
- `name` (optional) — display name for the asset. If `null`, server derives from the upload.
- `parentFolderId` (optional) — UUID of a folder in the tenant. If `null`, the asset lands at tenant root.

**Response shape (HTTP 200):**

```json
{
  "data": {
    "requestUpload": {
      "assetId": "1a2b3c4d-...",
      "jobId":   "5e6f7g8h-...",
      "expectedBlobUrl": "https://<storage>.blob.core.windows.net/uploads/<tenant>/<asset>/<job>.sog",
      "sasUrl":          "https://<storage>.blob.core.windows.net/uploads/<tenant>/<asset>/<job>.sog?<sas-token>"
    }
  }
}
```

- `sasUrl` is the URL you `PUT` the bytes to in Step 2. **Valid for 2 hours.**
- `expectedBlobUrl` is the same URL without the SAS query string — useful for logging.
- `assetId` and `jobId` are UUIDs you can use to track processing.

**curl example:**

```bash
curl -s -X POST "$APTIXAR_BASE_URL/integrationgraphql/" \
  -H "Authorization: Bearer $APTIXAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($fileExt: String!) { requestUpload(fileExt: $fileExt) }",
    "variables": {"fileExt": "sog"}
  }'
```

---

## Step 2: `PUT` to the SAS URL

**Required header:**

| Header | Value |
|---|---|
| `x-ms-blob-type` | `BlockBlob` |

**Do NOT** send `Authorization: Bearer ...` on this request — the SAS URL carries its own credential in the query string. Adding your PAT header is wrong (and ignored by Azure, but still: don't).

**curl example:**

```bash
curl -s -X PUT "$SAS_URL" \
  -H "x-ms-blob-type: BlockBlob" \
  --data-binary @/path/to/scene.sog
```

Successful response: HTTP 201 (with empty body).

---

## Step 3: Server-side processing

Once the `PUT` succeeds, Aptixar's IMPORT processor (selected automatically based on `fileExt`) picks up the upload, converts it as needed, and attaches the result to the asset created in Step 1. The partner sees the asset appear in the web portal under the chosen folder (or tenant root) once processing completes.

There is currently no integration-API endpoint to poll job status; check the web portal, or watch for the asset to appear with its preview rendered.

---

## End-to-end curl example

Assumes `APTIXAR_BASE_URL` and `APTIXAR_TOKEN` are exported.

```bash
# Step 1: requestUpload
RESP=$(curl -s -X POST "$APTIXAR_BASE_URL/integrationgraphql/" \
  -H "Authorization: Bearer $APTIXAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($fileExt: String!) { requestUpload(fileExt: $fileExt) }",
    "variables": {"fileExt": "sog"}
  }')

# Extract sasUrl with jq (or your preferred JSON tool)
SAS_URL=$(echo "$RESP" | jq -r '.data.requestUpload.sasUrl')

# Step 2: PUT the file
curl -s -X PUT "$SAS_URL" \
  -H "x-ms-blob-type: BlockBlob" \
  --data-binary @/path/to/scene.sog

echo "Upload complete. Check the web portal."
```
