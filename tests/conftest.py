import pytest
from pathlib import Path

@pytest.fixture
def sample_warninglist(tmp_path: Path) -> Path:
    wl_file = tmp_path / "warninglist.json"
    wl_file.write_text('{"domain": ["example.test"], "ipv4": ["192.0.2.10"]}', encoding="utf-8")
    return wl_file