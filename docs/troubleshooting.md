# Troubleshooting

## HTTP 401 on `requestUpload`

The token is missing, malformed, or the server doesn't recognize it.

- Verify the header is exactly `Authorization: Bearer aptx_int_<...>` (note the space after `Bearer`).
- Verify the token starts with `aptx_int_` and has 32 characters after the prefix.
- Tokens are tenant-scoped. Verify the token was minted in the same Aptixar tenant whose data you expect the upload to land in.

## HTTP 403 on `requestUpload`

The token resolves but the server is refusing.

- The token may lack the `upload` scope. Check in the web portal under Settings → Integrations.
- The token may be revoked or expired. Mint a new one.

## `requestUpload` returns a name-length error or `Internal server error.`

The most common cause is an asset `name` longer than 64 characters. The server rejects it and creates nothing. The error text may be specific (`Ensure this value has at most 64 characters`) or generic.

- Shorten the name to 64 characters or fewer. Length is counted in characters, not bytes. See [asset-names.md](asset-names.md).
- If the name is short enough, contact your Aptixar representative with the request time and the `name` you sent.

## HTTP 403 on the `PUT` to `sasUrl`

The SAS URL expired (2-hour window) or the query string was modified.

- Call `requestUpload` again to get a fresh `sasUrl`.
- Use the exact URL from the response — don't url-encode the query string or strip parameters.

## HTTP 400 on the `PUT` to `sasUrl`

Almost always a missing `x-ms-blob-type: BlockBlob` header.

- Add the header. It is required by Azure Blob Storage for block-blob PUTs.

## Upload succeeds, but no asset appears in the portal

The Aptixar IMPORT processor may have rejected the file (corrupt, unsupported variant of the extension, etc.).

- Open `https://www.aptixar.com/assets?assetId=<assetId>` — it distinguishes "still processing" from "this upload failed", and shows the failure reason when the server recorded one. See [upload-flow.md](upload-flow.md#the-view-link).
- Contact your Aptixar representative with the `jobId` and `assetId` from the `requestUpload` response.

## The view link says the asset could not be found

`assetId` must be an asset id from a `requestUpload` response. A snapshot id pasted in its place will not resolve — use `?id=<snapshotId>` for a specific scene instead.

Assets are also tenant-scoped: the link only resolves for someone signed in to the same Aptixar organization the token belongs to, with permission to view scenes.
