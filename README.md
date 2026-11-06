# SMSMobileAPI + Telegram

Connect your own Telegram account to SMSMobileAPI and send text messages from the dashboard or an HTTPS API. This repository contains a focused API contract and a step-by-step guide.

## What you can do

- Connect one Telegram account per SMSMobileAPI account by scanning a QR code in the Telegram mobile app.
- Synchronize contacts and saved `@username` entries, then search them by name or username.
- Queue a text message to a contact through the dashboard or `POST /telegram/send/`.
- Inspect the sending status and errors through `GET /telegram/sent/`.
- Keep requests scoped to each customer's connected account and control endpoint access from **My API Key**.

Telegram receiving, media sending, recipient delivery receipts, and read receipts are not exposed by these endpoints today.

## Start in five steps

1. Create or sign in to a [SMSMobileAPI account](https://smsmobileapi.com/signup/).
2. Open [Telegram connection](https://dashboard.smsmobileapi.com/telegram-connect/) and scan the QR code from **Telegram → Settings → Devices → Link Desktop Device**.
3. Open [Telegram contacts](https://dashboard.smsmobileapi.com/telegram-contacts/) and synchronize your contacts.
4. Copy your key from [My API Key](https://dashboard.smsmobileapi.com/my-api-key/) and store it as a server-side secret.
5. [Send a message in the dashboard](https://dashboard.smsmobileapi.com/telegram-send/) or call the API. Check the [sending log](https://dashboard.smsmobileapi.com/telegram-logs/) afterward.

## API at a glance

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/telegram/contacts/` | Search and page through synchronized contacts |
| POST | `/telegram/send/` | Queue one text message to a `contact_id` |
| GET | `/telegram/sent/` | Check queued, sending, sent, error or unknown status |

Base URL: `https://api.smsmobileapi.com`. Authenticate all three requests with the `X-SMSMobileAPI-Key: YOUR_API_KEY` header. A successful HTTP 202 send response means **queued**. It does not mean recipient delivery.

The complete walkthrough, curl requests, response examples, limits, and errors are in [docs/telegram.md](docs/telegram.md). The machine-readable contract is [openapi.yaml](openapi.yaml).

## Example API request

Once you have synchronized contacts and found a `contact_id`, queue one text message:

```bash
curl -X POST 'https://api.smsmobileapi.com/telegram/send/' \
  -H 'X-SMSMobileAPI-Key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"contact_id":42,"message":"Your appointment is confirmed."}'
```

The API returns a `message_id`. Use `GET /telegram/sent/?message_id=123` to check its status. See the [full guide](docs/telegram.md) for contact lookup, retries and response examples.

## Operational limits

The current limit is 15 new messages per minute and 30 queued messages per connected account. Use the sending log to distinguish `queued`, `sending`, `sent`, `error`, and `unknown`. `sent` means Telegram accepted the send; delivery and read receipts are unavailable. Avoid blind retries after an `unknown` outcome.

Keep your SMSMobileAPI key out of source control, public clients, and screenshots. Respect Telegram rules and recipient consent.

## Links

- [Telegram product overview](https://smsmobileapi.com/telegram/)
- [Interactive Telegram API documentation](https://smsmobileapi.com/doc-telegram/)
- [Full SMSMobileAPI OpenAPI specification](https://github.com/SmsMobileApi/smsmobileapi-openapi)
- [SMSMobileAPI support](https://dashboard.smsmobileapi.com/support/)

MIT licensed. Telegram is a trademark of its respective owner; this is an SMSMobileAPI integration repository.
