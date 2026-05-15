# Python reference client

A small Python implementation of the Aptixar upload protocol. The `aptixar_uploader` package wraps the two-step flow (GraphQL `requestUpload` → Azure Blob `PUT`) into one method call.

If you're building in a non-Python language, read [`../docs/upload-flow.md`](../docs/upload-flow.md) — that's the canonical protocol spec. This package is one working implementation of it.

## Install

From this `python/` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

The package depends on `requests` and `python-dotenv`. Both will be installed automatically.

## Configure

From the repository root (one level up):

```bash
cp .env.template .env
# then edit .env and paste your APTIXAR_TOKEN
```

## Run the CLI

```bash
python -m aptixar_uploader upload /path/to/scene.sog
```

Optional flags:

```bash
python -m aptixar_uploader upload /path/to/scene.sog \
  --name "Building 4, Floor 2" \
  --folder <parent-folder-uuid>
```

## Use as a library

```python
from aptixar_uploader import AptixarClient

client = AptixarClient.from_env()
result = client.upload_file("/path/to/scene.sog", name="Building 4")
print(result.asset_id, result.job_id)
```

`AptixarClient.from_env()` reads `APTIXAR_BASE_URL` (defaulting to `https://dev.aptixar.com`) and `APTIXAR_TOKEN` from the environment, loading `.env` in the current working directory if present.

## Run the examples

The `examples/` directory has three increasingly contextual scripts:

- `01_minimal_upload.py` — the smallest possible end-to-end script.
- `02_upload_to_folder.py` — adds `parentFolderId` targeting.
- `03_xgrids_lcc2_upload.py` — XGRIDS LCC Studio post-export hook variant.

Run any of them after `pip install -e .` and a valid `.env`.

## Run the tests

```bash
pip install -e ".[dev]"
pytest
```

All tests mock HTTP — no real network access. Run them anywhere.
