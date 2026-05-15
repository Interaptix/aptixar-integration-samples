"""XGRIDS LCC Studio integration: push a .sog or .lcc2 file to Aptixar after export.

This is the script you'd run from your post-export hook (or wire into LCC Studio's
"publish to Aptixar" path) once an XGRIDS scan is ready to share.

Usage:
    python 03_xgrids_lcc2_upload.py /path/to/export.sog [scene_name]

Notes:
  - The Aptixar IMPORT processor accepts both .sog (Gaussian splat) and .lcc2
    (XGRIDS native bundle). File extension determines how it's processed.
  - The scene_name is what appears in the Aptixar web portal asset list.
    Omit to let the server name it after the file.
  - If you want everything from a given XGRIDS project to land in a specific
    folder, set APTIXAR_PARENT_FOLDER_ID in your .env file.
"""

import os
import sys

from aptixar_uploader import AptixarClient


def main() -> None:
    if not 2 <= len(sys.argv) <= 3:
        sys.exit("usage: python 03_xgrids_lcc2_upload.py <file> [scene_name]")

    file_path = sys.argv[1]
    scene_name = sys.argv[2] if len(sys.argv) == 3 else None
    folder_id = os.environ.get("APTIXAR_PARENT_FOLDER_ID") or None

    client = AptixarClient.from_env()
    result = client.upload_file(
        file_path,
        name=scene_name,
        parent_folder_id=folder_id,
    )

    print("XGRIDS scan handed off to Aptixar.")
    print(f"  file: {file_path}")
    print(f"  assetId: {result.asset_id}")
    print(f"  jobId:   {result.job_id}")
    print("  Open the Aptixar web portal to watch the IMPORT processor finish.")


if __name__ == "__main__":
    main()
