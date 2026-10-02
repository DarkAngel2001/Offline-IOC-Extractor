import json
from pathlib import Path

def load_warning_values(path: str | Path) -> dict[str, set[str]]:
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    return {
        item_type: {value.lower() for value in values}
        for item_type, values in data.items()
    }

def warning_flags(
    value: str,
    indicator_type: str,
    warning_values: dict[str, set[str]],
) -> bool:
    return value.lower() in warning_values.get(indicator_type, set())