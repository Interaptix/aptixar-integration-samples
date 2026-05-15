# Aptixar Integration Samples

Sample code and documentation showing how to push files into Aptixar from a third-party integration.

The protocol is documented language-agnostically in [`docs/`](docs/). A working Python reference lives in [`python/`](python/). If you're building in another language, read the docs and port the protocol — it's intentionally small (two HTTP calls).

## Quickstart

1. **Get a token.** Ask an Aptixar tenant admin to mint one for you in the web portal (Settings → Integrations). See [`docs/authentication.md`](docs/authentication.md) for the full flow.
2. **Configure.**
   ```bash
   cp .env.template .env
   # edit .env and paste your APTIXAR_TOKEN
   ```
3. **Install and run the Python sample.**
   ```bash
   cd python
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   python -m aptixar_uploader upload /path/to/scene.sog
   ```

## The upload flow

Two HTTP calls:

1. `POST {APTIXAR_BASE_URL}/integrationgraphql/` with a `requestUpload` GraphQL mutation. Server returns a temporary Azure Blob SAS URL.
2. `PUT` the file bytes to that SAS URL.

Full protocol with curl examples: [`docs/upload-flow.md`](docs/upload-flow.md).

## Dev vs prod

Edit `APTIXAR_BASE_URL` in your `.env`:

- **Dev** — `https://dev.aptixar.com`
- **Prod** — `https://aptixar.com`

Tokens are environment-specific. A dev token will not work against prod.

## Repository layout

```
.
├── .env.template          # copy to .env, fill in your token
├── docs/                  # language-agnostic protocol spec
│   ├── authentication.md
│   ├── upload-flow.md
│   ├── file-types.md
│   └── troubleshooting.md
└── python/                # Python reference implementation
    ├── aptixar_uploader/  # the importable package
    ├── examples/          # 01_minimal, 02_folder, 03_xgrids_lcc2
    └── tests/
```

## Issues

File issues on this repo on GitHub. Include the `jobId` and `assetId` from your `requestUpload` response when reporting an upload that fails server-side.
