import os

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
]


# Ollama models

OLLAMA_CLASSIFY_MODEL = os.getenv("OLLAMA_CLASSIFY_MODEL", "phi3:mini")
OLLAMA_DRAFT_MODEL = os.getenv("OLLAMA_DRAFT_MODEL", "phi3:mini")


# Ollama runtime parameters

OLLAMA_CLASSIFY_OPTIONS = {
    "temperature": float(os.getenv("OLLAMA_CLASSIFY_TEMPERATURE", "0.0")),
    "num_ctx": int(os.getenv("OLLAMA_CLASSIFY_NUM_CTX", "4096")),
    "num_predict": int(os.getenv("OLLAMA_CLASSIFY_NUM_PREDICT", "120")),
}

OLLAMA_DRAFT_OPTIONS = {
    "temperature": float(os.getenv("OLLAMA_DRAFT_TEMPERATURE", "0.2")),
    "num_ctx": int(os.getenv("OLLAMA_DRAFT_NUM_CTX", "8192")),
    "num_predict": int(os.getenv("OLLAMA_DRAFT_NUM_PREDICT", "350")),
}


# Gmail behaviour

GMAIL_QUERY = os.getenv("GMAIL_QUERY", "label:LENAH is:unread")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes", "y")
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "10"))
