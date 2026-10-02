from email import policy
from email.parser import BytesParser
from pathlib import Path

TEXT_SUFFIXES = {".txt", ".log", ".csv", ".json", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MiB

def read_text_file(path: str) -> str:
    p = Path(path)
    if p.is_dir():
        raise ValueError(f"Path is a directory: {path}")
    if p.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds maximum allowed size of 10 MiB: {path}")
    return p.read_text(encoding="utf-8", errors="replace")

def read_eml_file(path: str) -> str:
    p = Path(path)
    if p.is_dir():
        raise ValueError(f"Path is a directory: {path}")
    if p.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds maximum allowed size of 10 MiB: {path}")

    with open(path, "rb") as file:
        message = BytesParser(policy=policy.default).parse(file)

    parts = [
        str(message.get("subject", "")),
        str(message.get("from", "")),
        str(message.get("to", "")),
        str(message.get("cc", "")),
    ]

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                continue
            if part.get_content_type() == "text/plain":
                try:
                    content = part.get_content()
                    if isinstance(content, str):
                        parts.append(content)
                except (LookupError, UnicodeDecodeError):
                    continue
    elif message.get_content_type() == "text/plain":
        content = message.get_content()
        if isinstance(content, str):
            parts.append(content)

    return "\n".join(part for part in parts if part)

def read_artifact(path: str) -> tuple[str, str]:
    suffix = Path(path).suffix.lower()

    if suffix == ".eml":
        return read_eml_file(path), "eml"

    if suffix in TEXT_SUFFIXES:
        return read_text_file(path), "text"

    raise ValueError(
        f"Unsupported file type: {suffix or '<no extension>'}. "
        "Only text files and .eml are supported."
    )