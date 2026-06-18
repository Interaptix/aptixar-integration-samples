#!/usr/bin/env bash
# Authenticated requestUpload smoke for the Aptixar integration API.
# Proves: the token authenticates and the server returns a SAS URL.
# Does NOT upload any bytes (the SAS URL is never consumed).
#
# Env:
#   APTIXAR_TOKEN     (required) integration PAT, upload scope
#   APTIXAR_BASE_URL  (optional) default https://api.aptixar.com
#   CI_ASSET_ID       (optional) pin requestUpload to one reusable asset;
#                     if unset, the server creates one asset (bootstrap)
set -euo pipefail

BASE_URL="${APTIXAR_BASE_URL:-https://api.aptixar.com}"
: "${APTIXAR_TOKEN:?APTIXAR_TOKEN is required}"
ASSET_ID="${CI_ASSET_ID:-}"

if [ -n "$ASSET_ID" ]; then
  query='mutation($fileExt:String!,$assetId:ID){requestUpload(fileExt:$fileExt,assetId:$assetId)}'
  variables=$(jq -nc --arg f splat --arg a "$ASSET_ID" '{fileExt:$f,assetId:$a}')
else
  query='mutation($fileExt:String!){requestUpload(fileExt:$fileExt)}'
  variables=$(jq -nc --arg f splat '{fileExt:$f}')
fi
body=$(jq -nc --arg q "$query" --argjson v "$variables" '{query:$q,variables:$v}')

resp=$(curl -sS --max-time 30 --connect-timeout 10 -w $'\n%{http_code}' -X POST "$BASE_URL/integrationgraphql/" \
  -H "Authorization: Bearer $APTIXAR_TOKEN" \
  -H 'Content-Type: application/json' \
  -d "$body")
status=$(printf '%s' "$resp" | tail -n1)
payload=$(printf '%s' "$resp" | sed '$d')

echo "HTTP $status"

if [ "$status" != "200" ]; then
  echo "FAIL: expected HTTP 200, got $status" >&2
  printf '%s' "$payload" | head -c 300 >&2; echo >&2
  exit 1
fi

if ! printf '%s' "$payload" | jq -e . >/dev/null 2>&1; then
  echo "FAIL: response is not JSON (likely routed to the wrong origin)" >&2
  printf '%s' "$payload" | head -c 120 >&2; echo >&2
  exit 1
fi

if printf '%s' "$payload" | jq -e '(.errors // []) | length > 0' >/dev/null 2>&1; then
  echo "FAIL: GraphQL errors:" >&2
  printf '%s' "$payload" | jq -c '.errors' >&2
  exit 1
fi

sas=$(printf '%s' "$payload" | jq -r '.data.requestUpload.sasUrl // empty')
if [ -z "$sas" ]; then
  echo "FAIL: no sasUrl in response" >&2
  exit 1
fi

asset=$(printf '%s' "$payload" | jq -r '.data.requestUpload.assetId // empty')
job=$(printf '%s' "$payload" | jq -r '.data.requestUpload.jobId // empty')
echo "OK: requestUpload succeeded (assetId=$asset jobId=$job)"
# sasUrl intentionally not printed — it is a credential.
