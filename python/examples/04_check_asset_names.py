"""Check asset names before publishing: what the portal will show, or why it fails.

Runs offline -- no token, no upload. Pass your own names, or run it bare to see
the sample set.

Usage:
    python 04_check_asset_names.py ["name one" "name two" ...]

The rules are in ../../docs/asset-names.md. In short: any Unicode text up to
64 characters (counted in characters, not bytes); < > " \\ / | ? * become "-".
"""

import sys

from aptixar_uploader import check_asset_name

SAMPLE_NAMES = [
    "Building 4, Floor 2",           # spaces and punctuation
    "一号楼 二层 扫描",                 # Chinese
    "Plant (North) [v2]",            # parentheses and brackets
    "scan-2026-11-19_area_03",       # hyphens and underscores
    "Line 3 / Station 7?",           # reserved characters
    "扫" * 64,                        # 64 characters, 192 bytes: fits
    "x" * 65,                        # 65 characters: rejected
]


def main() -> None:
    names = sys.argv[1:] or SAMPLE_NAMES
    failed = False
    for name in names:
        try:
            shown = check_asset_name(name)
        except ValueError as e:
            failed = True
            print(f"REJECTED  {e}")
            continue
        note = "" if shown == name else "  (reserved characters replaced)"
        print(f"OK        {name!r} -> {shown!r}{note}")
    sys.exit(1 if failed and sys.argv[1:] else 0)


if __name__ == "__main__":
    main()
