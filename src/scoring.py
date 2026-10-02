CONTEXT_RADIUS = 80

POSITIVE_CONTEXT = {
    "malicious",
    "phishing",
    "c2",
    "command-and-control",
    "observed",
    "indicator",
    "payload",
}

NEGATIVE_CONTEXT = {
    "example",
    "documentation",
    "test",
    "training",
    "placeholder",
}

DOCUMENTATION_DOMAINS = {"example.test", "example.com", "example.org", "example.net"}
DOCUMENTATION_IPS = {"192.0.2.", "198.51.100.", "203.0.113."}

def nearby_context(text: str, start: int, end: int) -> str:
    left = max(0, start - CONTEXT_RADIUS)
    right = min(len(text), end + CONTEXT_RADIUS)
    return " ".join(text[left:right].split())

def score_indicator(value: str, type_str: str, context: str | None, warning_matched: bool) -> tuple[str, list[str]]:
    score = 50
    flags = []

    val_lower = value.lower()
    if type_str == "domain" and val_lower in DOCUMENTATION_DOMAINS:
        flags.append("documentation_domain")
        score -= 30
    elif type_str == "ipv4" and any(val_lower.startswith(prefix) for prefix in DOCUMENTATION_IPS):
        flags.append("documentation_range")
        score -= 30

    if warning_matched:
        flags.append("warninglist_match")
        score -= 20

    if context:
        ctx_lower = context.lower()
        if any(pos in ctx_lower for pos in POSITIVE_CONTEXT):
            score += 25
        if any(neg in ctx_lower for neg in NEGATIVE_CONTEXT):
            score -= 30

    score = max(0, min(100, score))

    if score >= 70:
        confidence = "high"
    elif score >= 30:
        confidence = "medium"
    else:
        confidence = "low"

    return confidence, flags