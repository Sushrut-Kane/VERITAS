"""Evaluate generated Delivery-Format output against the worked ground-truth rows.

Matches by Mfg_Part_Num and reports, per field: exact-match %, description
char-limit compliance, and attribute (label,value) precision/recall. Honest by
design — where the input row carries no evidence for a field, a low score is the
correct, expected signal (not something to paper over).

    python scripts/evaluate_against_ground_truth.py \
        --input "New/Unihack_ Sample Dataset - Input.csv" \
        --expected "New/Unihack_ Expected Output - Delivery Format.csv"
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.catalog.delivery import build_delivery_row  # noqa: E402
from app.catalog.enrich import enrich_row  # noqa: E402
from app.catalog.ingest import read_catalog_rows  # noqa: E402

COMPARE_FIELDS = [
    "MANUFACTURER_NAME",
    "BRAND_NAME",
    "Product Name",
    "INVOICE_DESC",
    "MOBILE_DESC",
    "SHORT_DESC",
    "RETAIL_DESC",
    "LONG_DESC1",
]


def _norm(text: str) -> str:
    return " ".join((text or "").split()).strip().lower()


def _attr_pairs(row: dict) -> set[tuple[str, str]]:
    pairs = set()
    for i in range(1, 51):
        label = _norm(row.get(f"ATTRIBUTE_LABEL {i}", ""))
        value = _norm(row.get(f"ATTRIBUTE_VALUE {i}", ""))
        if label or value:
            pairs.add((label, value))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--expected", required=True)
    args = parser.parse_args()

    input_rows = {r.mfg_part_num: r for r in read_catalog_rows(args.input)}
    with open(args.expected, newline="", encoding="utf-8-sig") as handle:
        expected_rows = list(csv.DictReader(handle))

    field_hits = {f: 0 for f in COMPARE_FIELDS}
    invoice_ok = mobile_ok = 0
    attr_prec_sum = attr_rec_sum = 0.0
    compared = 0

    for expected in expected_rows:
        part = (expected.get("Mfg_Part_Num") or "").strip()
        row = input_rows.get(part)
        if row is None:
            print(f"[skip] {part}: not present in input")
            continue
        compared += 1
        generated = build_delivery_row(row, enrich_row(row))

        for field in COMPARE_FIELDS:
            if _norm(generated.get(field, "")) == _norm(expected.get(field, "")):
                field_hits[field] += 1

        if len(generated.get("INVOICE_DESC", "")) <= 40:
            invoice_ok += 1
        if 60 <= len(generated.get("MOBILE_DESC", "")) <= 80:
            mobile_ok += 1

        gen_attrs, exp_attrs = _attr_pairs(generated), _attr_pairs(expected)
        overlap = len(gen_attrs & exp_attrs)
        attr_prec_sum += overlap / len(gen_attrs) if gen_attrs else 0.0
        attr_rec_sum += overlap / len(exp_attrs) if exp_attrs else 0.0

    if compared == 0:
        print("No rows compared.")
        return

    print(f"\nCompared {compared} row(s) against ground truth.\n")
    print("Exact-match rate per field:")
    for field in COMPARE_FIELDS:
        print(f"  {field:<22} {field_hits[field] / compared:6.0%}")
    print("\nDescription char-limit compliance (generated):")
    print(f"  INVOICE_DESC <= 40      {invoice_ok / compared:6.0%}")
    print(f"  MOBILE_DESC in 60-80    {mobile_ok / compared:6.0%}")
    print("\nAttribute (label,value) overlap:")
    print(f"  precision               {attr_prec_sum / compared:6.0%}")
    print(f"  recall                  {attr_rec_sum / compared:6.0%}")


if __name__ == "__main__":
    main()
