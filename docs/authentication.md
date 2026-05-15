# Authentication

The Aptixar Integration API uses Personal Access Tokens (PATs). Each token belongs to a single tenant and carries one or more scopes. Currently only the `upload` scope is supported.

## Who creates the token

The token is minted by an **Aptixar tenant admin**, not by the partner. The admin shares the token with the partner through a secure channel.

## Minting a token

1. Sign in to the Aptixar web portal (`https://dev.aptixar.com` for dev, `https://aptixar.com` for prod).
2. Open **Settings → Integrations**.
3. Click **New Integration**.
4. Fill in:
   - **Name:** a label for the integration (e.g. `XGRIDS LCC Studio`).
   - **Scopes:** check `upload`.
   - **Expires at (optional):** an expiry date. Tokens without an expiry never expire automatically — set one if you can.
5. Click **Create**. The plaintext token is shown **once**. Copy it immediately and store it somewhere safe (password manager, secret store, CI variable). Aptixar does not retain the plaintext; if you lose it you must rotate.

## Token format

```
aptx_int_<32 base62 chars>
```

The `aptx_int_` prefix tells the server this is an integration PAT.

## Using the token

Send it on every API call as a Bearer header:

```
Authorization: Bearer aptx_int_<your-token>
```

## Rotating / revoking

- **Rotate:** Settings → Integrations → the row → **Rotate**. Generates a new plaintext (shown once). The old plaintext immediately stops working.
- **Revoke:** Settings → Integrations → the row → **Revoke**. The token is dead; partners using it will get HTTP 401 / 403.

## Security notes

- Tokens grant tenant-scoped write access. Treat them like passwords.
- Do not check `.env` files into source control.
- Do not log the token, the `sasUrl` from `requestUpload` responses, or any header beginning with `Authorization`.
- Set an expiry whenever you can. Rotate on a schedule.
