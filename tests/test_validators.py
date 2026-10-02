import pytest
from src.validators import (
    is_valid_domain,
    is_valid_hash,
    is_valid_ipv4,
    is_valid_url,
    is_valid_email,
)

@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("192.0.2.10", True),
        ("999.1.2.3", False),
        ("1.2.3", False),
        ("01.2.3.4", False),
    ],
)
def test_ipv4_validation(value, expected):
    assert is_valid_ipv4(value) is expected

@pytest.mark.parametrize(
    ("value", "length", "expected"),
    [
        ("a" * 32, 32, True),
        ("a" * 40, 40, True),
        ("a" * 64, 64, True),
        ("g" * 64, 64, False),
        ("a" * 63, 64, False),
    ],
)
def test_hash_validation(value, length, expected):
    assert is_valid_hash(value, length) is expected

def test_domain_validation():
    assert is_valid_domain("example.test")
    assert is_valid_domain("Example.TEST.")
    assert not is_valid_domain("bad_domain.test")

def test_url_validation():
    assert is_valid_url("https://example.test/path")
    assert not is_valid_url("ftp://example.test")
    assert not is_valid_url("https://user:pass@example.test")

def test_email_validation():
    assert is_valid_email("analyst@example.test")
    assert not is_valid_email("plain-string")