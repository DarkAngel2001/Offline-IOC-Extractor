import re

TRAILING_PUNCTUATION = '.,;:!?)]}\'\"'

def clean_candidate(value: str) -> str:
    return value.rstrip(TRAILING_PUNCTUATION).strip()

def refang(value: str) -> tuple[str, str | None]:
    original = value
    normalized = re.sub(r"(?i)\bhxxps://", "https://", value)
    normalized = re.sub(r"(?i)\bhxxp://", "http://", normalized)
    normalized = normalized.replace("[.]", ".").replace("(.)", ".")
    normalized = normalized.replace("[://]", "://")

    if normalized != original:
        return normalized, original
    return normalized, None

def normalize_email(value: str) -> str:
    return value.strip().lower()

def normalize_domain(value: str) -> str:
    return value.strip().lower().rstrip(".")

def normalize_hash(value: str) -> str:
    return value.strip().lower()