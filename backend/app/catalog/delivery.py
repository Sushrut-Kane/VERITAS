"""Map an EnrichedProduct onto the frozen 252-column Delivery Format row.

Any field VERITAS cannot fill from evidence is left blank rather than guessed —
honest gaps (per the Solution Guide) are expected, not a bug.
"""
import csv

from app.catalog.columns import DELIVERY_COLUMNS, MAX_ATTRIBUTES, MAX_ITEM_FEATURES
from app.catalog.models import CatalogRow, EnrichedProduct


def build_delivery_row(row: CatalogRow, product: EnrichedProduct) -> dict[str, str]:
    data = {col: "" for col in DELIVERY_COLUMNS}

    # Echo the original input identity columns unchanged.
    data["Mfg_Part_Num"] = row.mfg_part_num
    data["Part_Desc"] = row.part_desc
    data["E1_Brand"] = row.e1_brand
    data["Unilog_Brand"] = row.unilog_brand
    data["DIB_Brand"] = row.dib_brand
    data["Part_Manuf"] = row.part_manuf

    data["PART_NUMBER"] = product.part_number
    data["MANUFACTURER_PART_NUMBER"] = product.part_number
    data["MANUFACTURER_NAME"] = product.manufacturer_name
    data["BRAND_NAME"] = product.brand_name
    data["Classpath"] = product.classpath

    data["MOBILE_DESC"] = product.mobile_desc
    data["INVOICE_DESC"] = product.invoice_desc
    data["SHORT_DESC"] = product.short_desc
    data["LONG_DESC1"] = product.long_desc
    data["RETAIL_DESC"] = product.retail_desc
    data["MARKETING_DESCRIPTION"] = product.marketing_desc
    data["Product Name"] = product.product_name

    for idx, feature in enumerate(product.item_features[:MAX_ITEM_FEATURES], start=1):
        data[f"ITEM_FEATURES_{idx}"] = feature

    for idx, attr in enumerate(product.attributes[:MAX_ATTRIBUTES], start=1):
        data[f"ATTRIBUTE_LABEL {idx}"] = attr.label
        data[f"ATTRIBUTE_VALUE {idx}"] = attr.value
        data[f"ATTRIBUTE_UOM {idx}"] = attr.uom

    return data


def row_to_list(data: dict[str, str]) -> list[str]:
    return [data.get(col, "") for col in DELIVERY_COLUMNS]


def write_delivery_csv(rows: list[dict[str, str]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(DELIVERY_COLUMNS)
        for data in rows:
            writer.writerow(row_to_list(data))


# ---------------------------------------------------------------------------
# QA export: frozen 252 + review metadata appended at the end
# ---------------------------------------------------------------------------

QA_COLUMNS: list[str] = DELIVERY_COLUMNS + ["_NEEDS_REVIEW", "_REVIEW_REASONS"]


def build_qa_row(row: CatalogRow, product: EnrichedProduct) -> dict[str, str]:
    """Delivery row + review metadata appended (never reorders the 252)."""
    data = build_delivery_row(row, product)
    data["_NEEDS_REVIEW"] = "TRUE" if product.needs_review else "FALSE"
    data["_REVIEW_REASONS"] = "; ".join(product.review_reasons)
    return data


def row_to_qa_list(data: dict[str, str]) -> list[str]:
    return [data.get(col, "") for col in QA_COLUMNS]


def write_qa_csv(rows: list[dict[str, str]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(QA_COLUMNS)
        for data in rows:
            writer.writerow(row_to_qa_list(data))

