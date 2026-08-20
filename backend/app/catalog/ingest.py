"""Read the input catalog CSV, enrich each row, and build Delivery-Format rows."""
import csv

from app.catalog.delivery import build_delivery_row, write_delivery_csv
from app.catalog.enrich import enrich_row
from app.catalog.models import CatalogRow, EnrichedProduct


def read_catalog_rows(path: str) -> list[CatalogRow]:
    rows: list[CatalogRow] = []
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for index, record in enumerate(reader):
            rows.append(
                CatalogRow(
                    mfg_part_num=(record.get("Mfg_Part_Num") or "").strip(),
                    part_desc=(record.get("Part_Desc") or "").strip(),
                    e1_brand=(record.get("E1_Brand") or "").strip(),
                    unilog_brand=(record.get("Unilog_Brand") or "").strip(),
                    dib_brand=(record.get("DIB_Brand") or "").strip(),
                    part_manuf=(record.get("Part_Manuf") or "").strip(),
                    row_index=index,
                )
            )
    return rows


def enrich_rows(
    rows: list[CatalogRow], limit: int | None = None
) -> list[tuple[CatalogRow, EnrichedProduct]]:
    selected = rows[:limit] if limit else rows
    return [(row, enrich_row(row)) for row in selected]


def run_ingest(input_path: str, output_path: str, limit: int | None = None) -> int:
    rows = read_catalog_rows(input_path)
    pairs = enrich_rows(rows, limit=limit)
    delivery_rows = [build_delivery_row(row, product) for row, product in pairs]
    write_delivery_csv(delivery_rows, output_path)
    return len(delivery_rows)
