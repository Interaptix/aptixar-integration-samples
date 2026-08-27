# Upload flow

This is the canonical protocol document. The Python reference in `../python/` implements exactly this flow; partners on other stacks can read this file and port the protocol directly.

## Overview

Uploading a file to Aptixar takes three steps:

1. **Admin creates an integration token** — see [authentication.md](authentication.md).
2. **Partner calls `requestUpload`** — a GraphQL mutation that returns a temporary Azure Blob SAS URL.
3. **Partner `PUT`s the file** to that SAS URL.

The server creates the asset record when you call `requestUpload` (you get back its `assetId` immediately). Once the PUT completes, the server's IMPORT processor takes over and attaches a snapshot — previews, mesh files, etc. — to that asset.

The `assetId` is also all you need to build a [view link](#the-view-link) for the scene, so a link can be published before the file has even been uploaded.

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
- `assetId` is the id of the asset the upload lands in. It is what a [view link](#the-view-link) is built from, and what you quote when reporting a problem.
- `jobId` identifies this particular upload of it.

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

There is currently no integration-API endpoint to poll job status. Open the [view link](#the-view-link) instead — it reports whether the upload is still processing, and shows the scene once it isn't.

---

## The view link

`requestUpload` hands back an `assetId`. That is all you need to build a link that opens the scene in the Aptixar web portal:

```
https://www.aptixar.com/assets?assetId=<assetId>
```

Build and publish it **as soon as `requestUpload` returns** — before the `PUT`, and without waiting for processing. It keys off the asset rather than the processed scene, so there is no second id to wait for and nothing to poll.

What the link does depends on where the upload has got to:

| State | What the visitor sees |
|---|---|
| Processing finished | The asset's newest scene, same as clicking it in the portal. |
| Still processing | A progress message. The page switches itself to the scene when processing completes — no refresh needed. |
| Upload failed | A message saying so, with the reason when the server recorded one. |
| Nothing uploaded yet | A message saying so — distinct from the failure case. |

Two caveats worth knowing before you publish links:

- **It is not an anonymous share link.** It opens for anyone signed in to your Aptixar organization with permission to view scenes; anyone else is asked to sign in.
- **`assetId` must be an asset id.** A snapshot id will not resolve here — to link a specific scene rather than the newest one, use `?id=<snapshotId>`. Both ids are shown in a scene's details dialog in the portal.

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

# Extract sasUrl and assetId with jq (or your preferred JSON tool)
SAS_URL=$(echo "$RESP" | jq -r '.data.requestUpload.sasUrl')
ASSET_ID=$(echo "$RESP" | jq -r '.data.requestUpload.assetId')

# Step 2: PUT the file
curl -s -X PUT "$SAS_URL" \
  -H "x-ms-blob-type: BlockBlob" \
  --data-binary @/path/to/scene.sog

echo "Upload complete. View: https://www.aptixar.com/assets?assetId=$ASSET_ID"
```
