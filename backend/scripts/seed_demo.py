"""Seed the 3-beat demo dataset and run it through the real pipeline.

Requires Postgres + Neo4j to be up (``docker compose up -d db neo4j`` and
``alembic upgrade head``). No Anthropic API key needed — claims are pre-seeded so
the pipeline runs its deterministic offline path end to end.

    python scripts/seed_demo.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select  # noqa: E402

from app.agents.graph_pipeline import pipeline  # noqa: E402
from app.db.models.attribute import Attribute  # noqa: E402
from app.db.models.audit_log import AuditLog  # noqa: E402
from app.db.models.document import DocType, Document, DocumentStatus  # noqa: E402
from app.db.models.product import Product  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.graph.client import close_driver  # noqa: E402
from app.schemas.pipeline_state import ExtractedClaim, PipelineState  # noqa: E402

DEMO_SKU = "VRT-PUMP-3000"


def _claim(attr_key, raw, unit, span):
    return ExtractedClaim(
        attr_key=attr_key,
        attr_value=str(raw),
        raw_value=str(raw),
        unit=unit,
        source_span=span,
        extraction_confidence=0.95,
    )


# Beat 1: clean spec sheet. Beat 2: second source with a unit-only match
# (176 degF == 80 degC -> derived, not conflicting) and a genuine conflict
# (voltage 110 V vs 230 V -> conflicting).
DOC_A_CLAIMS = [
    _claim("max_operating_temp", 80, "°C", "Max Operating Temperature: 80 °C"),
    _claim("voltage_rating", 230, "V", "Rated Voltage: 230 V"),
    _claim("weight", 12, "kg", "Weight: 12 kg"),
    _claim("housing_material", "Stainless Steel 316", None, "Housing Material: Stainless Steel 316"),
    _claim("pressure_rating", 10, "bar", "Max Pressure: 10 bar"),
]

DOC_B_CLAIMS = [
    _claim("max_operating_temp", 176, "°F", "Operating temp up to 176 °F"),
    _claim("weight", 12, "kg", "Net weight 12 kg"),
    _claim("voltage_rating", 110, "V", "Supply: 110 V"),
    _claim("noise_level", 60, "dB", "Noise level: 60 dB"),
]


async def _reset_demo(session):
    result = await session.execute(select(Product).where(Product.sku == DEMO_SKU))
    product = result.scalar_one_or_none()
    if product is None:
        return
    doc_ids = (
        await session.execute(
            select(Document.id).where(Document.product_id == product.id)
        )
    ).scalars().all()
    if doc_ids:
        await session.execute(delete(AuditLog).where(AuditLog.document_id.in_(doc_ids)))
    await session.execute(delete(Attribute).where(Attribute.product_id == product.id))
    await session.execute(delete(Document).where(Document.product_id == product.id))
    await session.execute(delete(Product).where(Product.id == product.id))
    await session.commit()


async def _run_document(product_id, sku, filename, claims):
    async with AsyncSessionLocal() as session:
        document = Document(
            product_id=product_id,
            filename=filename,
            doc_type=DocType.pdf_spec,
            storage_path=f"./uploads/demo/{filename}",
            status=DocumentStatus.processing,
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)
        document_id = document.id

    state = PipelineState(
        document_id=document_id,
        product_id=product_id,
        product_sku=sku,
        doc_type="pdf_spec",
        raw_claims=claims,
    )
    await pipeline.ainvoke(state.model_dump())

    async with AsyncSessionLocal() as session:
        doc = await session.get(Document, document_id)
        doc.status = DocumentStatus.done
        await session.commit()


async def _print_summary(product_id):
    async with AsyncSessionLocal() as session:
        rows = (
            await session.execute(
                select(Attribute)
                .where(Attribute.product_id == product_id)
                .order_by(Attribute.attr_key)
            )
        ).scalars().all()

    print(f"\nDemo product {DEMO_SKU} — {len(rows)} attribute rows:\n")
    print(f"{'attr_key':<20} {'value':<22} {'class':<12} {'policy':<14}")
    print("-" * 70)
    for row in rows:
        value = f"{row.attr_value} {row.unit or ''}".strip()
        classification = row.classification.value if row.classification else "-"
        policy = row.policy_decision.value if row.policy_decision else "-"
        print(f"{row.attr_key:<20} {value:<22} {classification:<12} {policy:<14}")


async def main():
    async with AsyncSessionLocal() as session:
        await _reset_demo(session)
        product = Product(sku=DEMO_SKU, name="VERITAS Industrial Pump 3000")
        session.add(product)
        await session.commit()
        await session.refresh(product)
        product_id = product.id

    await _run_document(product_id, DEMO_SKU, "spec_sheet_A.pdf", DOC_A_CLAIMS)
    await _run_document(product_id, DEMO_SKU, "spec_sheet_B.pdf", DOC_B_CLAIMS)
    await _print_summary(product_id)
    await close_driver()


if __name__ == "__main__":
    asyncio.run(main())
