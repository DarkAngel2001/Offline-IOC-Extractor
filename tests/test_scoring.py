from src.scoring import score_indicator

def test_scoring_basics():
    conf, flags = score_indicator("192.0.2.10", "ipv4", "observed malicious payload", False)
    assert "documentation_range" in flags