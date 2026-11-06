#!/usr/bin/env python3
"""List Telegram contacts, queue a text message, and inspect its sending status.

Requires Python 3.11+ and SMSMOBILEAPI_API_KEY in the environment.
Only the explicit "send" subcommand queues a message.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE_URL = "https://api.smsmobileapi.com"


def api_request(method, path, *, params=None, payload=None):
    api_key = os.environ.get("SMSMOBILEAPI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set SMSMOBILEAPI_API_KEY before calling the API.")

    url = BASE_URL + path
    if params:
        values = {key: value for key, value in params.items() if value is not None}
        if values:
            url += "?" + urllib.parse.urlencode(values)

    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"X-SMSMobileAPI-Key": api_key, "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        print(f"HTTP {error.code}: {detail}", file=sys.stderr)
        raise SystemExit(1) from error
    except urllib.error.URLError as error:
        print(f"Request failed: {error.reason}", file=sys.stderr)
        raise SystemExit(1) from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    contacts = commands.add_parser("contacts", help="List synchronized contacts")
    contacts.add_argument("--query", default=None, help="Search name or @username")
    contacts.add_argument("--limit", type=int, default=50)
    contacts.add_argument("--cursor", type=int, default=None)

    send = commands.add_parser("send", help="Queue one text message")
    send.add_argument("contact_id", type=int, help="ID from the contacts endpoint")
    send.add_argument("message", help="UTF-8 text to send")
    send.add_argument(
        "--idempotency-key",
        default=None,
        help="Reuse a previously generated UUID when retrying the same message",
    )

    sent = commands.add_parser("sent", help="Inspect the sending log")
    sent.add_argument("--message-id", type=int, default=None)
    sent.add_argument("--contact-id", type=int, default=None)
    sent.add_argument(
        "--status",
        choices=("queued", "sending", "sent", "error", "unknown"),
        default=None,
    )
    sent.add_argument("--limit", type=int, default=50)
    sent.add_argument("--cursor", type=int, default=None)

    args = parser.parse_args()
    if args.command == "contacts":
        status, result = api_request(
            "GET",
            "/telegram/contacts/",
            params={"q": args.query, "limit": args.limit, "cursor": args.cursor},
        )
    elif args.command == "send":
        status, result = api_request(
            "POST",
            "/telegram/send/",
            payload={
                "contact_id": args.contact_id,
                "message": args.message,
                "idempotency_key": args.idempotency_key or str(uuid.uuid4()),
            },
        )
    else:
        status, result = api_request(
            "GET",
            "/telegram/sent/",
            params={
                "message_id": args.message_id,
                "contact_id": args.contact_id,
                "status": args.status,
                "limit": args.limit,
                "cursor": args.cursor,
            },
        )
    print(f"HTTP {status}")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
