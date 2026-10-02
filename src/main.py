import argparse
from pathlib import Path

from src.exporters import export_csv, export_json
from src.extractor import extract_from_file

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract validated IOCs from offline text artifacts."
    )
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--json", default="output/iocs.json")
    parser.add_argument("--csv", default="output/iocs.csv")
    parser.add_argument("--refang", action="store_true")
    parser.add_argument("--include-context", action="store_true")
    parser.add_argument("--warninglist", type=Path, default=None)
    return parser

def main() -> int:
    args = build_parser().parse_args()

    try:
        indicators = extract_from_file(
            str(args.input_file),
            refang_enabled=args.refang,
            include_context=args.include_context,
            warninglist_path=args.warninglist,
        )
    except Exception as e:
        print(f"Error processing artifact: {e}")
        return 1

    export_json(indicators, args.json)
    export_csv(indicators, args.csv)

    print(f"Extracted {len(indicators)} unique indicators.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())