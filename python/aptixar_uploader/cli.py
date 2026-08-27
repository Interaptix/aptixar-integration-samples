"""Command-line entry point for the aptixar-uploader package.

Usage:
    python -m aptixar_uploader upload <file> [--name NAME] [--folder FOLDER_ID]
"""

import argparse
import sys

from aptixar_uploader.client import AptixarClient


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aptixar-upload",
        description="Upload a file to Aptixar via the Integration API.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    upload = subparsers.add_parser("upload", help="Upload a single file.")
    upload.add_argument("file", help="Path to the file to upload.")
    upload.add_argument("--name", help="Asset name (defaults to filename).", default=None)
    upload.add_argument(
        "--folder",
        dest="parent_folder_id",
        help="Parent folder ID (defaults to APTIXAR_PARENT_FOLDER_ID env or tenant root).",
        default=None,
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    if args.command == "upload":
        try:
            client = AptixarClient.from_env()
            result = client.upload_file(
                args.file,
                name=args.name,
                parent_folder_id=args.parent_folder_id,
            )
        except (RuntimeError, FileNotFoundError, ValueError) as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"assetId: {result.asset_id}")
        print(f"jobId:   {result.job_id}")
        print(f"viewUrl: {result.view_url}")
        print("Uploaded. The link above works now; it reports progress until processing finishes.")
