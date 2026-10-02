import ipaddress
import re
from urllib.parse import urlparse

DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)"
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z]{2,63}$",
    re.IGNORECASE,
)

EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
)

def is_valid_ipv4(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return isinstance(address, ipaddress.IPv4Address)

def is_valid_domain(value: str) -> bool:
    normalized = value.lower().rstrip(".")
    return bool(DOMAIN_RE.fullmatch(normalized))

def is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme.lower() in {"http", "https"}
            and bool(parsed.netloc)
            and not parsed.username
            and not parsed.password
        )
    except ValueError:
        return False

def is_valid_email(value: str) -> bool:
    return bool(EMAIL_RE.fullmatch(value))

def is_valid_hash(value: str, length: int) -> bool:
    return bool(re.fullmatch(rf"[0-9a-fA-F]{{{length}}}", value))