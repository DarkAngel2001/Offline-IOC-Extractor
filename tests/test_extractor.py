from src.extractor import extract_from_file

def test_extract_synthetic(tmp_path):
    report = tmp_path / "report.txt"
    report.write_text(
        "Observed IP: 192.0.2.10\nDomain: example.test\nEmail: analyst@example.test",
        encoding="utf-8"
    )
    indicators = extract_from_file(str(report))
    values = {i.value for i in indicators}
    assert "192.0.2.10" in values
    assert "example.test" in values
    assert "analyst@example.test" in values