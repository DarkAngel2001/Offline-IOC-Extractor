import pytest
from src.readers import read_text_file

def test_read_text_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world", encoding="utf-8")
    assert read_text_file(str(f)) == "hello world"