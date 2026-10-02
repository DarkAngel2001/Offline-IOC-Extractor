from dataclasses import asdict, dataclass
from typing import Any

@dataclass(frozen=True)
class Indicator:
    value: str
    type: str
    confidence: str
    source_file: str
    source_kind: str = "text"
    line: int | None = None
    column: int | None = None
    context: str | None = None
    flags: tuple[str, ...] = ()
    normalized_from: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["flags"] = list(self.flags)
        return result