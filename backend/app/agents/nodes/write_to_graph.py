"""write_to_graph node: persist every normalized claim into Neo4j.

A claim_id (uuid4) is generated here so Postgres and Neo4j reference the same id.
"""
import uuid

from app.core.logging import get_logger
from app.db.models.document import Document
from app.db.session import AsyncSessionLocal
from app.graph import queries
from app.schemas.pipeline_state import PipelineState

logger = get_logger(__name__)


async def write_to_graph(state: PipelineState) -> dict:
    async with AsyncSessionLocal() as session:
        document = await session.get(Document, state.document_id)
    filename = document.filename if document else str(state.document_id)
    doc_type = document.doc_type.value if document else state.doc_type

    updated = []
    for claim in state.normalized_claims:
        claim_id = claim.claim_id or uuid.uuid4()
        await queries.write_claim(
            sku=state.product_sku,
            attr_key=claim.attr_key,
            claim_id=claim_id,
            value=claim.attr_value,
            confidence=claim.extraction_confidence,
            doc_id=state.document_id,
            filename=filename,
            doc_type=doc_type,
        )
        updated.append(claim.model_copy(update={"claim_id": claim_id}))

    logger.info("write_to_graph_done", count=len(updated))
    return {"normalized_claims": updated, "status": "written_to_graph"}
