import os

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
]

OLLAMA_CLASSIFY_MODEL = os.getenv("OLLAMA_CLASSIFY_MODEL", "phi3:mini")
OLLAMA_DRAFT_MODEL = os.getenv("OLLAMA_DRAFT_MODEL", "phi3:mini")

GMAIL_QUERY = os.getenv("GMAIL_QUERY", "label:LENAH is:unread")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes", "y")
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "10"))
