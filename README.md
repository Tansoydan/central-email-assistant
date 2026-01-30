# LENAH – Centralised Email Assistant (Gmail + Local LLM)

LENAH is a **centralised email assistant** designed to triage and respond to incoming emails using a local Large Language Model (LLM).  
This proof of concept demonstrates how a shared inbox (e.g. `enquiries@company.com`) can be monitored, filtered, classified, and replied to **safely and audibly** without auto-sending emails.

The system is built with **Python**, the **Gmail API**, and a **local Ollama LLM**, with guardrails in place to ensure only relevant emails reach the model.

---

## 🎯 Project Objectives

- Connect to a **centralised LENAH Gmail inbox**
- Process only emails with a specific **Gmail label**
- Apply a **pre-filter layer** to block newsletters, promotions, and forwards
- Classify relevant emails using a **local LLM (Ollama)**
- Decide whether a reply is required
- Generate a **Gmail draft** (not auto-sent)
- Log all decisions for **auditability**

---

## 🧠 High-Level Architecture

```
Gmail Inbox (LENAH ID)
        |
   Gmail Label
        |
   Gmail API
        |
   Pre-filter Layer
        |
   Local Ollama LLM
   (classification + drafting)
        |
   Gmail Drafts
        |
   Audit Logs
```

---

## 🛡️ Safety & Guardrails

- **Label-based access**: only emails explicitly labelled `LENAH` are processed
- **Pre-filtering** blocks:
  - newsletters
  - promotions
  - forwards
  - marketing emails
- **Dry-run mode** enabled by default (no drafts created)
- Emails are **never auto-sent**
- All actions are logged for traceability

---

## 🧰 Tech Stack

- **Python 3.9+**
- **Gmail API** (read + draft permissions only)
- **Ollama** (local LLM runtime)
- **phi3 / similar lightweight LLMs**
- Google OAuth 2.0

---

## 📁 Project Structure

```
central-email-assistant/
├── main.py
├── credentials.json
├── token.json
├── runs/
│   └── run_YYYYMMDD_HHMMSS.jsonl
└── src/
    ├── gmail_client.py
    ├── ollama_client.py
    ├── prefilter.py
    ├── audit.py
    ├── config.py
```

---

## ⚙️ Configuration

All runtime configuration is managed in `src/config.py`.

Example:

```python
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

GMAIL_QUERY = "label:LENAH is:unread"
MAX_RESULTS = 10

OLLAMA_CLASSIFY_MODEL = "phi3:mini"
OLLAMA_DRAFT_MODEL = "phi3:mini"

DRY_RUN = True
```

---

## ▶️ How It Works

1. Authenticate with Gmail using OAuth
2. Fetch emails matching the `LENAH` label
3. Apply a **pre-filter** to remove unwanted emails
4. Send relevant emails to the LLM for classification
5. Decide whether a reply is needed
6. Generate a **draft reply** (dry-run by default)
7. Log the full decision trail to a JSONL audit file

---

## 🧪 Running the Project

Activate your virtual environment:

```bash
source .venv/bin/activate
```

Run the assistant:

```bash
python main.py
```

You should see console output showing:
- emails fetched
- pre-filter decisions
- LLM classification
- draft previews (in dry-run mode)

---

## 📝 Audit Logging

Each run produces a timestamped audit log in the `runs/` directory, including:
- message ID
- classification results
- pre-filter decisions
- whether a draft was created
- dry-run status

This ensures the system is **transparent and reviewable**.

---

## 📌 Summary

This project demonstrates a **safe, auditable, and scalable** approach to using LLMs for email automation.  
By combining Gmail labels, rule-based pre-filtering, and a local LLM, LENAH provides a strong foundation for real-world deployment in property and customer enquiry workflows.
