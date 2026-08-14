import uuid

import pytest
from sqlalchemy import select

from app.agents.graph_pipeline import pipeline
from app.db.models.attribute import Attribute
from app.db.models.document import DocType, Document, DocumentStatus
from app.db.models.product import Product
from app.db.session import AsyncSessionLocal
from app.schemas.pipeline_state import ExtractedClaim, PipelineState


async def _seed_product_and_document(sku: str) -> tuple[Product, Document]:
    async with AsyncSessionLocal() as session:
        product = Product(sku=sku, name="Test Pump")
        session.add(product)
        await session.flush()
        document = Document(
            product_id=product.id,
            filename="spec.pdf",
            doc_type=DocType.pdf_spec,
            storage_path="/tmp/spec.pdf",
            status=DocumentStatus.processing,
        )
        session.add(document)
        await session.commit()
        await session.refresh(product)
        await session.refresh(document)
        return product, document


def _claim(attr_key: str, raw: str, unit: str | None, span: str) -> ExtractedClaim:
    return ExtractedClaim(
        attr_key=attr_key,
        attr_value=raw,
        raw_value=raw,
        unit=unit,
        source_span=span,
        extraction_confidence=0.95,
    )


@pytest.mark.asyncio
async def test_pipeline_publishes_clean_and_reviews_safety(graph_store):
    product, document = await _seed_product_and_document("PUMP-CLEAN")
    state = PipelineState(
        document_id=document.id,
        product_id=product.id,
        product_sku=product.sku,
        doc_type="pdf_spec",
        raw_claims=[
            _claim("weight", "10", "kg", "Weight: 10 kg"),
            _claim("voltage_rating", "230", "V", "Rated voltage: 230 V"),
        ],
    )

    await pipeline.ainvoke(state.model_dump())

    async with AsyncSessionLocal() as session:
        rows = (
            await session.execute(
                select(Attribute).where(Attribute.product_id == product.id)
            )
        ).scalars().all()

    by_key = {row.attr_key: row for row in rows}
    assert by_key["weight"].classification.value == "verified"
    assert by_key["weight"].policy_decision.value == "publish"
    # Safety-critical attributes always route to human review.
    assert by_key["voltage_rating"].policy_decision.value == "human_review"


@pytest.mark.asyncio
async def test_pipeline_flags_cross_document_conflict(graph_store):
    product, document = await _seed_product_and_document("PUMP-CONFLICT")
    # Pre-existing, contradicting claim already in the evidence graph.
    await graph_store.write_claim(
        sku="PUMP-CONFLICT",
        attr_key="weight",
        claim_id=uuid.uuid4(),
        value="10",
        confidence=0.9,
        doc_id=uuid.uuid4(),
        filename="old_spec.pdf",
        doc_type="pdf_spec",
    )

    state = PipelineState(
        document_id=document.id,
        product_id=product.id,
        product_sku=product.sku,
        doc_type="pdf_spec",
        raw_claims=[_claim("weight", "25", "kg", "Weight: 25 kg")],
    )
    await pipeline.ainvoke(state.model_dump())

    async with AsyncSessionLocal() as session:
        row = (
            await session.execute(
                select(Attribute).where(
                    Attribute.product_id == product.id, Attribute.attr_key == "weight"
                )
            )
        ).scalars().first()

    assert row is not None
    assert row.classification.value == "conflicting"
    assert row.policy_decision.value == "human_review"
    assert graph_store.contradict_edges  # a CONTRADICTS edge was recorded
