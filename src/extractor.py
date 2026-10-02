import re
from src.models import Indicator
from src.readers import read_artifact
from src.normalizers import clean_candidate, refang, normalize_email, normalize_domain, normalize_hash
from src.validators import is_valid_ipv4, is_valid_domain, is_valid_url, is_valid_email, is_valid_hash
from src.scoring import score_indicator, nearby_context
from src.warninglists import load_warning_values, warning_flags

MARKDOWN_LINK_RE = re.compile(
    r"\[[^\]\n]{1,500}\]\((https?://[^)\s]+|mailto:[^)>\s]+)\)",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://[^\s<>\"']+|hxxps?://[^\s<>\"']+", re.IGNORECASE)
EMAIL_RE = re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
IPV4_RE = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
HASH_RE = re.compile(r"\b[0-9a-fA-F]{32}\b|\b[0-9a-fA-F]{40}\b|\b[0-9a-fA-F]{64}\b")
DOMAIN_RE = re.compile(r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}\b", re.IGNORECASE)

def mask_spans(text: str, spans: list[tuple[int, int]]) -> str:
    chars = list(text)
    for start, end in spans:
        for index in range(start, end):
            if chars[index] != "\n":
                chars[index] = " "
    return "".join(chars)

def extract_from_file(
    path: str,
    *,
    refang_enabled: bool = False,
    include_context: bool = False,
    warninglist_path: str | None = None,
) -> list[Indicator]:
    content, source_kind = read_artifact(path)
    warning_values = load_warning_values(warninglist_path) if warninglist_path else {}

    raw_text = content
    spans_to_mask = []

    extracted_records: list[dict] = []

    # 1. Markdown Links & Ordinary URLs
    for match in MARKDOWN_LINK_RE.finditer(raw_text):
        spans_to_mask.append((match.start(), match.end()))
        full_match = match.group(1)
        if full_match.lower().startswith("mailto:"):
            email_val = full_match[7:]
            cleaned = clean_candidate(email_val)
            norm_email = normalize_email(cleaned)
            if is_valid_email(norm_email):
                line = raw_text.count("\n", 0, match.start()) + 1
                col = match.start() - raw_text.rfind("\n", 0, match.start())
                extracted_records.append({
                    "value": norm_email,
                    "type": "email",
                    "source_file": path,
                    "source_kind": source_kind,
                    "line": line,
                    "column": col,
                    "context": nearby_context(raw_text, match.start(), match.end()) if include_context else None,
                    "flags": ("appears_in_url",),
                    "normalized_from": None,
                })
        else:
            cleaned = clean_candidate(full_match)
            norm_val, orig = (cleaned, None)
            if refang_enabled:
                norm_val, orig = refang(cleaned)
            if is_valid_url(norm_val):
                line = raw_text.count("\n", 0, match.start()) + 1
                col = match.start() - raw_text.rfind("\n", 0, match.start())
                extracted_records.append({
                    "value": norm_val,
                    "type": "url",
                    "source_file": path,
                    "source_kind": source_kind,
                    "line": line,
                    "column": col,
                    "context": nearby_context(raw_text, match.start(), match.end()) if include_context else None,
                    "flags": ("defanged",) if orig else (),
                    "normalized_from": orig,
                })

    for match in URL_RE.finditer(raw_text):
        spans_to_mask.append((match.start(), match.end()))
        cleaned = clean_candidate(match.group(0))
        norm_val, orig = (cleaned, None)
        if refang_enabled:
            norm_val, orig = refang(cleaned)
        if is_valid_url(norm_val):
            line = raw_text.count("\n", 0, match.start()) + 1
            col = match.start() - raw_text.rfind("\n", 0, match.start())
            extracted_records.append({
                "value": norm_val,
                "type": "url",
                "source_file": path,
                "source_kind": source_kind,
                "line": line,
                "column": col,
                "context": nearby_context(raw_text, match.start(), match.end()) if include_context else None,
                "flags": ("defanged",) if orig else (),
                "normalized_from": orig,
            })

    masked_for_emails = mask_spans(raw_text, spans_to_mask)

    # 2. Emails
    email_spans = []
    for match in EMAIL_RE.finditer(masked_for_emails):
        email_spans.append((match.start(), match.end()))
        cleaned = clean_candidate(match.group(0))
        norm_email = normalize_email(cleaned)
        if is_valid_email(norm_email):
            line = raw_text.count("\n", 0, match.start()) + 1
            col = match.start() - raw_text.rfind("\n", 0, match.start())
            extracted_records.append({
                "value": norm_email,
                "type": "email",
                "source_file": path,
                "source_kind": source_kind,
                "line": line,
                "column": col,
                "context": nearby_context(raw_text, match.start(), match.end()) if include_context else None,
                "flags": (),
                "normalized_from": None,
            })

    masked_for_hashes = mask_spans(masked_for_emails, email_spans)

    # 3. Hashes
    hash_spans = []
    for match in HASH_RE.finditer(masked_for_hashes):
        hash_spans.append((match.start(), match.end()))
        cleaned = clean_candidate(match.group(0))
        norm_hash = normalize_hash(cleaned)
        length = len(norm_hash)
        if is_valid_hash(norm_hash, length):
            htype = "md5" if length == 32 else ("sha1" if length == 40 else "sha256")
            line = raw_text.count("\n", 0, match.start()) + 1
            col = match.start() - raw_text.rfind("\n", 0, match.start())
            extracted_records.append({
                "value": norm_hash,
                "type": htype,
                "source_file": path,
                "source_kind": source_kind,
                "line": line,
                "column": col,
                "context": nearby_context(raw_text, match.start(), match.end()) if include_context else None,
                "flags": (),
                "normalized_from": None,
            })

    masked_for_ips = mask_spans(masked_for_hashes, hash_spans)

    # 4. IPv4
    ip_spans = []
    for match in IPV4_RE.finditer(masked_for_ips):
        ip_spans.append((match.start(), match.end()))
        cleaned = clean_candidate(match.group(0))
        if is_valid_ipv4(cleaned):
            line = raw_text.count("\n", 0, match.start()) + 1
            col = match.start() - raw_text.rfind("\n", 0, match.start())
            extracted_records.append({
                "value": cleaned,
                "type": "ipv4",
                "source_file": path,
                "source_kind": source_kind,
                "line": line,
                "column": col,
                "context": nearby_context(raw_text, match.start(), match.end()) if include_context else None,
                "flags": (),
                "normalized_from": None,
            })

    masked_for_domains = mask_spans(masked_for_ips, ip_spans)

    # 5. Domains
    for match in DOMAIN_RE.finditer(masked_for_domains):
        cleaned = clean_candidate(match.group(0))
        norm_domain = normalize_domain(cleaned)
        if is_valid_domain(norm_domain):
            line = raw_text.count("\n", 0, match.start()) + 1
            col = match.start() - raw_text.rfind("\n", 0, match.start())
            extracted_records.append({
                "value": norm_domain,
                "type": "domain",
                "source_file": path,
                "source_kind": source_kind,
                "line": line,
                "column": col,
                "context": nearby_context(raw_text, match.start(), match.end()) if include_context else None,
                "flags": (),
                "normalized_from": None,
            })

    # Deduplicate & Score
    seen = {}
    indicators = []
    for rec in extracted_records:
        key = (rec["value"], rec["type"], rec["source_file"])
        matched_wl = warning_flags(rec["value"], rec["type"], warning_values)
        confidence, score_flags = score_indicator(rec["value"], rec["type"], rec["context"], matched_wl)
        
        all_flags = tuple(sorted(list(set(rec["flags"] + tuple(score_flags)))))

        if key in seen:
            # Update existing record flags or keep first
            continue
        
        indicator = Indicator(
            value=rec["value"],
            type=rec["type"],
            confidence=confidence,
            source_file=rec["source_file"],
            source_kind=rec["source_kind"],
            line=rec["line"],
            column=rec["column"],
            context=rec["context"],
            flags=all_flags,
            normalized_from=rec["normalized_from"],
        )
        seen[key] = indicator

    indicators = sorted(list(seen.values()), key=lambda i: (i.type, i.value, i.source_file, i.line or 0))
    return indicators