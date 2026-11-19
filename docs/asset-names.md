# Asset names

The `name` you pass to `requestUpload` becomes the asset's name in the Aptixar web portal. The scan the upload produces gets the same name.

## Allowed characters

Any Unicode text: letters in any script (Chinese included), digits, spaces, parentheses and brackets, hyphens, underscores, other punctuation, and emoji.

## Reserved characters

These eight are replaced with a hyphen (`-`) in the asset name:

```
< > " \ / | ? *
```

The upload still succeeds. For example, `Line 3 / Station 7?` is shown as `Line 3 - Station 7-`.

The replacement applies to the asset name only; the scan keeps the name exactly as sent. Replace them yourself before calling `requestUpload` if you want the two to match. The Python client does this for you.

## Length

**64 characters at most**, counted in characters (Unicode code points), not bytes. 64 Chinese characters is accepted, even though that is 192 bytes of UTF-8.

Some emoji are made of several code points (flags, skin tones, combined emoji such as families) and count as more than one character.

A longer name makes `requestUpload` return a GraphQL error, and nothing is created. Don't rely on the error text: it can be the specific `Ensure this value has at most 64 characters (it has 65).` or a generic `Internal server error.`. Check the length before you call. The Python client checks it for you: `upload_file` raises `ValueError` before sending anything.

## No name

If `name` is omitted, `null`, or empty, the asset is named `Untitled Import YYYY-MM-DD HH:MM:SS` (UTC), and the scan is named `Upload <jobId>`.

## Checking names before you publish

The Python package exposes the same rules:

```python
from aptixar_uploader import check_asset_name

check_asset_name("一号楼 二层 (v2)")   # returns the name unchanged
check_asset_name("Line 3 / Station 7?")  # returns "Line 3 - Station 7-"
check_asset_name("x" * 65)               # raises ValueError
```

[`python/examples/04_check_asset_names.py`](../python/examples/04_check_asset_names.py) runs a list of names through it offline, with no token needed.
