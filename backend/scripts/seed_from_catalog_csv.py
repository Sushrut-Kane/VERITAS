"""Populate Supabase with products and attributes parsed from a catalog CSV.

Usage:
    python scripts/seed_from_catalog_csv.py --input "path/to/Unihack_ Sample Dataset - Input.csv" [--limit 100]
"""
import argparse
import asyncio
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select, delete
from app.db.session import AsyncSessionLocal
from app.db.models.product import Product
from app.db.models.document import Document, DocType, DocumentStatus
from app.db.models.attribute import Attribute, Classification, PolicyDecision
from app.catalog.ingest import read_catalog_rows
from app.catalog.enrich import enrich_row


async def seed_from_csv(csv_path: Path, limit: int | None = None) -> None:
    print(f"Reading catalog rows from {csv_path}...")
    catalog_rows = read_catalog_rows(str(csv_path))
    if limit is not None:
        catalog_rows = catalog_rows[:limit]

    print(f"Enriching and inserting {len(catalog_rows)} products into database...")

    async with AsyncSessionLocal() as session:
        inserted_products = 0
        inserted_attributes = 0
        seen_skus = set()

        # Pre-fetch existing SKUs
        existing_res = await session.execute(select(Product.sku))
        seen_skus = {row[0] for row in existing_res.all()}

        products_to_add = []
        docs_to_add = []
        attrs_to_add = []

        for row in catalog_rows:
            sku = row.mfg_part_num.strip()
            if not sku or sku in seen_skus:
                continue
            seen_skus.add(sku)

            enriched = enrich_row(row)
            product_name = enriched.product_name or enriched.product_type or sku
            product_id = uuid.uuid4()
            doc_id = uuid.uuid4()

            product = Product(
                id=product_id,
                sku=sku,
                name=product_name,
            )
            products_to_add.append(product)

            doc = Document(
                id=doc_id,
                product_id=product_id,
                filename=csv_path.name,
                doc_type=DocType.catalog,
                storage_path=str(csv_path),
                status=DocumentStatus.done,
            )
            docs_to_add.append(doc)

            for attr in enriched.attributes:
                policy = (
                    PolicyDecision.human_review
                    if enriched.needs_review
                    else PolicyDecision.publish
                )
                attr_obj = Attribute(
                    id=uuid.uuid4(),
                    product_id=product_id,
                    attr_key=attr.label,
                    attr_value=attr.value,
                    raw_value=attr.value,
                    unit=attr.uom or None,
                    source_document_id=doc_id,
                    extraction_confidence=0.95,
                    classification=Classification.verified,
                    classification_confidence=0.95,
                    reasoning="; ".join(enriched.review_reasons) if enriched.review_reasons else None,
                    policy_decision=policy,
                )
                attrs_to_add.append(attr_obj)

            inserted_products += 1

        print(f"Adding {len(products_to_add)} products...")
        session.add_all(products_to_add)
        await session.flush()

        print(f"Adding {len(docs_to_add)} documents...")
        session.add_all(docs_to_add)
        await session.flush()

        print(f"Adding {len(attrs_to_add)} attributes...")
        session.add_all(attrs_to_add)
        await session.commit()
        print(f"Successfully populated database:")
        print(f"  - Products: {inserted_products}")
        print(f"  - Attributes: {len(attrs_to_add)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Populate Supabase database with catalog CSV products."
    )
    parser.add_argument("--input", required=True, help="Path to input catalog CSV")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of rows")
    args = parser.parse_args()

    asyncio.run(seed_from_csv(Path(args.input), limit=args.limit))


if __name__ == "__main__":
    main()
