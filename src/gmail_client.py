"""
Gmail API client for LENAH Assistant.

Provides functions to:
- Authenticate with Gmail API
- Fetch emails based on query
- Extract plain text from email bodies
- Create draft replies in Gmail

Key rule:
- Subject/From/Date/Reply-To are taken ONLY from Gmail headers.
- Header values are sanitised to remove embedded newlines and weird spacing.
"""

from __future__ import annotations

import os
import base64
from email.mime.text import MIMEText
from email.utils import parseaddr
from typing import Any, Dict, Iterator, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def authenticate_gmail(scopes: list[str]):
    creds: Optional[Credentials] = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _b64url_decode(data: str) -> str:
    if not data:
        return ""
    return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="replace")


def _walk_parts(payload: dict) -> Iterator[dict]:
    if not payload:
        return
    yield payload
    for part in payload.get("parts", []) or []:
        yield from _walk_parts(part)


def _clean_header_value(value: str) -> str:
    """
    Gmail header values can sometimes contain embedded newlines or folded whitespace.
    Make it safe for logs + downstream prompts.
    """
    if not value:
        return ""
    # Replace CR/LF with spaces, then collapse repeated whitespace
    value = value.replace("\r", " ").replace("\n", " ")
    value = " ".join(value.split())
    return value.strip()


def _get_header(headers: list[dict], name: str, default: str = "") -> str:
    target = name.lower()
    for h in headers:
        if (h.get("name") or "").lower() == target:
            return _clean_header_value(h.get("value") or "")
    return _clean_header_value(default)


def extract_plain_text_body(message: dict) -> str:
    payload = message.get("payload", {}) or {}
    best = ""

    for part in _walk_parts(payload):
        mime = (part.get("mimeType") or "").lower()
        body = part.get("body", {}) or {}
        data = body.get("data")

        if mime == "text/plain" and data:
            text = _b64url_decode(data).strip()
            if text:
                return text

        if not (part.get("parts") or []) and data and mime in ("text/plain", "text/html"):
            text = _b64url_decode(data).strip()
            if text:
                best = text

    return best.strip()


def fetch_emails(service, query: str, max_results: int) -> list[dict]:
    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )

    items = results.get("messages", []) or []
    if not items:
        return []

    emails: list[dict] = []

    for item in items:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=item["id"], format="full")
            .execute()
        )

        payload = msg.get("payload", {}) or {}
        headers = payload.get("headers", []) or []

        subject = _get_header(headers, "Subject", "No Subject")
        sender = _get_header(headers, "From", "Unknown Sender")
        date = _get_header(headers, "Date", "Unknown Date")
        reply_to = _get_header(headers, "Reply-To", "")

        snippet = (msg.get("snippet") or "").strip()
        body = extract_plain_text_body(msg).strip()
        text = body if body else snippet

        emails.append(
            {
                "id": item["id"],
                "threadId": msg.get("threadId"),
                "subject": subject,
                "from": sender,
                "reply_to": reply_to,
                "date": date,
                "snippet": snippet,
                "body": body,
                "text": text,
            }
        )

    return emails


def create_gmail_draft(service, email_data: dict, draft_body: str):
    reply_target = (email_data.get("reply_to") or "").strip() or (email_data.get("from") or "").strip()

    _, target_email = parseaddr(reply_target)
    to_addr = target_email if target_email else reply_target

    msg = MIMEText(draft_body)
    msg["to"] = to_addr

    subject = (email_data.get("subject") or "").strip()
    if subject.lower().startswith("re:"):
        msg["subject"] = subject
    else:
        msg["subject"] = f"Re: {subject}".strip()

    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    message_obj: Dict[str, Any] = {"raw": raw_message}
    if email_data.get("threadId"):
        message_obj["threadId"] = email_data["threadId"]

    draft = {"message": message_obj}

    created = (
        service.users()
        .drafts()
        .create(userId="me", body=draft)
        .execute()
    )
    return created

