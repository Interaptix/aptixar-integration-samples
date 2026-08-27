"""Upload a file into a specific folder.

Usage:
    python 02_upload_to_folder.py /path/to/scene.sog <parent_folder_id>

The folder ID is a UUID -- find it in the web portal URL when viewing a folder.
"""

import sys

from aptixar_uploader import AptixarClient


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: python 02_upload_to_folder.py <file> <parent_folder_id>")

    file_path = sys.argv[1]
    folder_id = sys.argv[2]

    client = AptixarClient.from_env()
    result = client.upload_file(
        file_path,
        name=None,  # defaults server-side based on the file
        parent_folder_id=folder_id,
    )

    print(f"Uploaded to folder {folder_id}.")
    print(f"  assetId={result.asset_id}")
    print(f"  jobId={result.job_id}")
    print(f"  view={result.view_url}")


if __name__ == "__main__":
    main()
