import re

BLOCK_FROM_PATTERNS = [
    r"\bnoreply\b", r"\bno-reply\b", r"\bdo-not-reply\b",
    r"\bnewsletter\b", r"\bjobalerts\b", r"\bmailer\b", r"\bmarketing\b",
    r"\bsurvey\b", r"\bresearch\b", r"\bopinium\b",
]

BLOCK_SUBJECT_PATTERNS = [
    r"\bverification\b", r"\bauthentication\b", r"\bsecurity\b", r"\bOTP\b", r"\bcode\b",
    r"\bdiscount\b", r"\boffer\b", r"\bsale\b", r"\bdeal\b", r"\blast chance\b",
    r"\bdigest\b", r"\bbriefing\b", r"\bnewsletter\b", r"\bjob alert\b",
    r"\bsurvey\b", r"\bprize\s*draw\b",
    r"\bwe(?:\s+would|\s*’d)\s+love\s+to\s+hear\s+from\s+you\b",
    r"\bcalling\s+for\b",
    r"\bexclusive\b", r"\blimited time\b", r"\bends today\b",r"\bpromotion\b",r"\bpromo\b",r"\bfree\b",r"\bsign\s*up\b"

]

ALLOW_HINT_PATTERNS = [
    r"\bview(?:ing)?\b",
    r"\bbook(?:ing)?\b",
    r"\bappointment\b",
    r"\bavailability\b",
    r"\benquir(?:y|ies)\b",
    r"\binterested\b",
    r"\bproperty\b",
    r"\bflat\b",
    r"\bhouse\b",
    r"\bpostcode\b",
    r"\brent\b",
    r"\blease\b",
    r"\btenanc(?:y|ies)\b",
    r"\bdeposit\b",
    r"\bmove(?:\s|-)?in\b",
    r"\bmove(?:\s|-)?out\b",
    r"\brepair\b",
    r"\bmaintenance\b",
    r"\bleak\b",
    r"\bbroken\b",
    r"\bkeys?\b",
    r"\bboiler\b",
    r"\bheating\b",
    r"\bmould\b",
    r"\bdamp\b",
    r"\bcomplaint\b",
    r"\brefund\b",
    r"\bcancel\b",
    r"\baddress\b",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t, flags=re.IGNORECASE) for p in patterns)


def prefilter_email(email_data: dict) -> tuple[bool, str]:
    sender = email_data.get("from", "")
    subject = email_data.get("subject", "")
    text = email_data.get("text", "")

    if _matches_any(sender, BLOCK_FROM_PATTERNS):
        return False, "blocked_sender_pattern"
    if _matches_any(subject, BLOCK_SUBJECT_PATTERNS):
        return False, "blocked_subject_pattern"
    if _matches_any(text, BLOCK_SUBJECT_PATTERNS):
        return False, "blocked_body_pattern"

    if _matches_any(subject, ALLOW_HINT_PATTERNS) or _matches_any(text, ALLOW_HINT_PATTERNS):
        return True, "allow_hint"

    return True, "default_candidate"

