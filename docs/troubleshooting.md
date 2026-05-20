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

## HTTP 403 on the `PUT` to `sasUrl`

The SAS URL expired (2-hour window) or the query string was modified.

- Call `requestUpload` again to get a fresh `sasUrl`.
- Use the exact URL from the response — don't url-encode the query string or strip parameters.

## HTTP 400 on the `PUT` to `sasUrl`

Almost always a missing `x-ms-blob-type: BlockBlob` header.

- Add the header. It is required by Azure Blob Storage for block-blob PUTs.

## Upload succeeds, but no asset appears in the portal

The Aptixar IMPORT processor may have rejected the file (corrupt, unsupported variant of the extension, etc.).

- Find the asset by `assetId` in the portal — there may be a processing-error state visible there.
- File an issue with the `jobId` and `assetId` from the `requestUpload` response.
