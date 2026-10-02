from src.exporters import export_json, export_csv
from src.models import Indicator

def test_exporters(tmp_path):
    ind = Indicator(
        value="192.0.2.10",
        type="ipv4",
        confidence="low",
        source_file="test.txt"
    )
    json_path = tmp_path / "out.json"
    csv_path = tmp_path / "out.csv"
    
    export_json([ind], json_path)
    export_csv([ind], csv_path)
    
    assert json_path.exists()
    assert csv_path.exists()