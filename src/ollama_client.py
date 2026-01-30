import ollama


def classify_email_with_ollama(email_data: dict, model: str) -> dict:
    prompt = f"""You are an email triage assistant.

Email Subject: {email_data.get('subject','')}
From: {email_data.get('from','')}
Content (truncated): {(email_data.get('text') or '')[:2000]}

Respond with ONLY these four lines (no extra text):
Category: [inquiry / complaint / general / ignore]
Priority: [high / medium / low / none]
Should_Reply: [yes / no]
Intent: [max 12 words, no commentary]

Rules:
- Newsletters, promotions, marketing, surveys, automated notifications, verification codes, job alerts, spam → Category: ignore and Should_Reply: no
- If you are not sure, choose Should_Reply: no
""".strip()

    resp = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    raw = (resp["message"]["content"] or "").strip()

    out = {
        "category": "general",
        "priority": "medium",
        "should_reply": "no",
        "intent": "Unknown",
        "raw": raw,
    }

    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    for line in lines:
        low = line.lower()
        if low.startswith("category:"):
            out["category"] = line.split(":", 1)[1].strip().lower()
        elif low.startswith("priority:"):
            out["priority"] = line.split(":", 1)[1].strip().lower()
        elif low.startswith("should_reply:"):
            out["should_reply"] = line.split(":", 1)[1].strip().lower()
        elif low.startswith("intent:"):
            out["intent"] = line.split(":", 1)[1].strip()

    # Safety net: never reply to obvious automated/marketing content, even if model says yes
    auto_signals = (
        "unsubscribe",
        "manage preferences",
        "newsletter",
        "promotion",
        "promo", 
        "sale ends",

    )
    blob = f"{email_data.get('subject','')} {email_data.get('from','')} {(email_data.get('text','') or '')[:4000]}".lower()
    if any(s in blob for s in auto_signals):
        out["category"] = "ignore"
        out["priority"] = "none"
        out["should_reply"] = "no"
        if not out["intent"] or out["intent"].lower() in ("unknown", ""):
            out["intent"] = "No action needed"

    # Normalise ignore category
    if out["category"] == "ignore":
        out["should_reply"] = "no"
        out["priority"] = "none"
        if not out["intent"] or out["intent"].lower() == "unknown":
            out["intent"] = "No action needed"

    # Normalise should_reply
    if out["should_reply"] not in ("yes", "no"):
        out["should_reply"] = "no"

    # Clamp intent length (prevents rambles)
    out["intent"] = (out["intent"] or "").strip()
    if len(out["intent"]) > 140:
        out["intent"] = out["intent"][:137].rstrip() + "..."

    return out



def generate_draft_reply_with_ollama(email_data: dict, classification: dict, model: str) -> str:
    prompt = f"""You are a professional email assistant.

Context:
- Category: {classification.get('category')}
- Priority: {classification.get('priority')}
- Intent: {classification.get('intent')}

Email:
Subject: {email_data.get('subject','')}
From: {email_data.get('from','')}
Content (truncated): {(email_data.get('text','') or '')[:2000]}

Write a professional, friendly reply email.
- Keep it concise and helpful
- Do not include a subject line, just the email body
- Do not invent facts or promises
- Mention a human will follow up if needed
- Sign off as "LENAH Assistant"
""".strip()

    resp = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return (resp["message"]["content"] or "").strip()
