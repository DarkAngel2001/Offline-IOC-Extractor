import csv
import json
from pathlib import Path
from src.models import Indicator

def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)

def build_summary(indicators: list[Indicator]) -> dict:
    by_type: dict[str, int] = {}
    by_confidence: dict[str, int] = {}
    for ind in indicators:
        by_type[ind.type] = by_type.get(ind.type, 0) + 1
        by_confidence[ind.confidence] = by_confidence.get(ind.confidence, 0) + 1
    return {
        "total": len(indicators),
        "by_type": by_type,
        "by_confidence": by_confidence,
    }

def export_json(indicators: list[Indicator], output_path: str | Path) -> None:
    path = Path(output_path)
    payload = {
        "indicators": [item.to_dict() for item in indicators],
        "summary": build_summary(indicators),
    }
    content = json.dumps(payload, indent=2, sort_keys=True)
    atomic_write(path, content)

CSV_HEADERS = [
    "value",
    "type",
    "confidence",
    "source_file",
    "source_kind",
    "line",
    "column",
    "context",
    "flags",
    "normalized_from",
]

def export_csv(indicators: list[Indicator], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = []
    # Using StringIO for deterministic CSV formatting
    import io
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(CSV_HEADERS)

    for ind in indicators:
        row = [
            ind.value,
            ind.type,
            ind.confidence,
            ind.source_file,
            ind.source_kind,
            ind.line if ind.line is not None else "",
            ind.column if ind.column is not None else "",
            ind.context if ind.context is not None else "",
            ";".join(ind.flags) if ind.flags else "",
            ind.normalized_from if ind.normalized_from is not None else "",
        ]
        writer.writerow(row)

    atomic_write(path, output.getvalue())