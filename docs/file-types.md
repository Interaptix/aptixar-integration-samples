# Supported file types

`fileExt` (no leading dot) tells the server how to process the upload. For partner integrations, you'll normally use the IMPORT pipeline (which is the default — you can omit `processorType`).

| `fileExt` | Default processor | What it produces |
|---|---|---|
| `sog` | `IMPORT` | Gaussian splat scene (XGRIDS export format) |
| `splat` | `IMPORT` | Gaussian splat scene |
| `lcc2` | `IMPORT` | XGRIDS LCC2 native scan bundle |
| `ply`  | `IMPORT` | Point cloud / mesh |
| `glb`  | `IMPORT` | glTF binary model |

Additional extensions are accepted as the IMPORT processor adds support; this table tracks the ones a partner is most likely to use today.

## What about `processorType`?

The `requestUpload` mutation accepts an optional `processorType`. **Leave it unset.** The server defaults to `IMPORT` for integration uploads, which is correct for partner integrations. The other types are internal to Aptixar's build pipeline and not appropriate for partner traffic. In particular: **never pass `BUILD_SPLAT`** — the server explicitly rejects it.
