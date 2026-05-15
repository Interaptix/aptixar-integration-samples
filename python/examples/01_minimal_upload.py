"""Minimal end-to-end Aptixar upload.

Usage:
    python 01_minimal_upload.py /path/to/scene.sog

Prereqs:
    1. Copy ../../.env.template to ../../.env and fill in APTIXAR_TOKEN.
    2. pip install -e .. (from the python/ directory).
"""

import sys

from aptixar_uploader import AptixarClient


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python 01_minimal_upload.py <file>")

    client = AptixarClient.from_env()
    result = client.upload_file(sys.argv[1])

    print(f"Uploaded. assetId={result.asset_id} jobId={result.job_id}")


if __name__ == "__main__":
    main()
