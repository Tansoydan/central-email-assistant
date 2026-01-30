import os
from datetime import datetime

from src.config import (
    SCOPES,
    OLLAMA_CLASSIFY_MODEL,
    OLLAMA_DRAFT_MODEL,
    GMAIL_QUERY,
    MAX_RESULTS,
    DRY_RUN,
)
from src.gmail_client import authenticate_gmail, fetch_emails, create_gmail_draft
from src.ollama_client import classify_email_with_ollama, generate_draft_reply_with_ollama
from src.prefilter import prefilter_email
from src.audit import ensure_runs_dir, log_jsonl


def main() -> None:
    print(" Starting LENAH Assistant")
    print(f"Query: {GMAIL_QUERY} | Max: {MAX_RESULTS} | Dry run: {DRY_RUN}")
    print("=" * 80)

    ensure_runs_dir()
    audit_path = os.path.join("runs", f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")

    service = authenticate_gmail(SCOPES)
    emails = fetch_emails(service, query=GMAIL_QUERY, max_results=MAX_RESULTS)

    print(f"Fetched: {len(emails)} email(s)\n")

    for i, e in enumerate(emails, start=1):
        print("-" * 80)
        print(f"[{i}/{len(emails)}] Subject: {e['subject']}")
        print(f"From: {e['from']}")
        print(f"Preview: {(e.get('text') or '')[:120].replace('\n', ' ')}")
        print("-" * 80)

        try:
            is_candidate, reason = prefilter_email(e)
            if not is_candidate:
                print(f"  Skipping LLM (prefilter): {reason}")
                log_jsonl(audit_path, {
                    "ts": datetime.now().isoformat(timespec="seconds"),
                    "message_id": e.get("id"),
                    "threadId": e.get("threadId"),
                    "subject": e.get("subject"),
                    "from": e.get("from"),
                    "query": GMAIL_QUERY,
                    "prefilter": {"candidate": False, "reason": reason},
                    "draft_created": False,
                    "draft_id": None,
                    "dry_run": DRY_RUN,
                })
                continue
            print("→ Calling LLM for classification...")
            classification = classify_email_with_ollama(e, model=OLLAMA_CLASSIFY_MODEL)
            print("✓ LLM classification returned")
            print("Classification:")
            print(f"  category     = {classification['category']}")
            print(f"  priority     = {classification['priority']}")
            print(f"  should_reply = {classification['should_reply']}")
            print(f"  intent       = {classification['intent']}")

            event = {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "message_id": e["id"],
                "threadId": e.get("threadId"),
                "subject": e["subject"],
                "from": e["from"],
                "query": GMAIL_QUERY,
                "prefilter": {"candidate": True, "reason": reason},
                "classification": {
                    "category": classification["category"],
                    "priority": classification["priority"],
                    "should_reply": classification["should_reply"],
                    "intent": classification["intent"],
                },
                "draft_created": False,
                "draft_id": None,
                "dry_run": DRY_RUN,
            }

            if classification["should_reply"] == "yes":
                draft_body = generate_draft_reply_with_ollama(e, classification, model=OLLAMA_DRAFT_MODEL)
                
                if DRY_RUN:
                    print("🟡 DRY_RUN: draft generated (not created in Gmail). Preview:")
                    print(draft_body[:400] + ("..." if len(draft_body) > 400 else ""))
                    event["draft_preview"] = draft_body[:800]
                    
                else:
                    created = create_gmail_draft(service, e, draft_body)
                    event["draft_created"] = True
                    event["draft_id"] = created.get("id")
                    print(f"✅ Draft created: {event['draft_id']}")

            log_jsonl(audit_path, event)

        except Exception as ex:
            print(f" Error processing email: {ex}")
            log_jsonl(audit_path, {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "message_id": e.get("id"),
                "subject": e.get("subject"),
                "from": e.get("from"),
                "error": str(ex),
            })

    print("\n" + "=" * 80)
    print(f"Done. Audit log: {audit_path}")
    if DRY_RUN:
        print("Dry run is ON. Set DRY_RUN=false to actually create drafts.")
    print("=" * 80)


if __name__ == "__main__":
    main()
