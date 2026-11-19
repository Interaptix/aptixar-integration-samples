"""Asset name rules for `requestUpload`'s `name`. See docs/asset-names.md."""

#: Longest name the server accepts, counted in characters (not bytes).
MAX_ASSET_NAME_LENGTH = 64

#: Characters the server replaces with REPLACEMENT_CHARACTER in asset names.
RESERVED_CHARACTERS = '<>"\\/|?*'
REPLACEMENT_CHARACTER = "-"


def check_asset_name(name: str) -> str:
    """Return `name` as the Aptixar portal will show it.

    Raises ValueError if the server would reject the name: longer than
    MAX_ASSET_NAME_LENGTH characters. Length is counted in characters, so 64
    Chinese characters is fine even though it is 192 bytes of UTF-8.

    Any other Unicode text is accepted as-is, including spaces, Chinese,
    parentheses, hyphens, underscores and emoji. The reserved characters
    < > " \\ / | ? * are each replaced with "-", as the server does.
    """
    if len(name) > MAX_ASSET_NAME_LENGTH:
        raise ValueError(
            f"Asset name is {len(name)} characters; the limit is "
            f"{MAX_ASSET_NAME_LENGTH}: {name!r}"
        )
    return "".join(
        REPLACEMENT_CHARACTER if ch in RESERVED_CHARACTERS else ch for ch in name
    )
