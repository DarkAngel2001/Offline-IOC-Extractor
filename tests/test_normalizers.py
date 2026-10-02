from src.normalizers import clean_candidate, refang

def test_clean_candidate():
    assert clean_candidate("https://example.test/path.") == "https://example.test/path"

def test_refang():
    norm, orig = refang("hxxps://example[.]test/login")
    assert norm == "https://example.test/login"
    assert orig == "hxxps://example[.]test/login"