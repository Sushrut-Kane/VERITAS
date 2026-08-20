"""CLI: enrich a messy catalog CSV into the 252-column Delivery Format.

    python scripts/ingest_catalog_csv.py --file input.csv --out delivery.csv [--limit N]

Runs fully offline (stdlib only) — no database, graph, or LLM key required.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.catalog.ingest import run_ingest  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enrich a catalog CSV into the 252-column Delivery Format."
    )
    parser.add_argument("--file", required=True, help="Path to the input catalog CSV")
    parser.add_argument("--out", required=True, help="Path to write the Delivery CSV")
    parser.add_argument(
        "--limit", type=int, default=None, help="Only process the first N rows"
    )
    args = parser.parse_args()

    count = run_ingest(args.file, args.out, limit=args.limit)
    print(f"Wrote {count} delivery rows to {args.out}")


if __name__ == "__main__":
    main()
