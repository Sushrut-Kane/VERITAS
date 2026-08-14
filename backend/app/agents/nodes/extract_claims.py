"""extract_claims node: LLM/VLM extraction into validated ExtractedClaim list.

Offline/seed path: if the incoming state already carries ``raw_claims`` (e.g. the
seed script or a test pre-populated them), they are validated and passed through
without an LLM call. Otherwise the document is read and sent to Claude.
"""
import base64
from pathlib import Path

from pydantic import ValidationError

from app.agents import llm
from app.agents.prompts.extraction_prompt import (
    EXTRACTION_SYSTEM_PROMPT,
    build_extraction_user_prompt,
)
from app.core.logging import get_logger
from app.db.models.document import DocType, Document
from app.db.session import AsyncSessionLocal
from app.schemas.pipeline_state import ExtractedClaim, PipelineState

logger = get_logger(__name__)

_IMAGE_MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


def _media_type_for(path: Path) -> str:
    return _IMAGE_MEDIA_TYPES.get(path.suffix.lower(), "image/png")


def _extract_pdf_text(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _validate_claims(raw_items: list[dict]) -> list[ExtractedClaim]:
    claims: list[ExtractedClaim] = []
    for item in raw_items:
        try:
            claim = ExtractedClaim.model_validate(item)
        except ValidationError as exc:
            logger.warning("claim_validation_failed", error=str(exc))
            continue
        if not claim.source_span or not claim.source_span.strip():
            # Hard requirement: never persist an unevidenced claim.
            logger.warning("claim_missing_source_span_dropped", attr_key=claim.attr_key)
            continue
        claims.append(claim)
    return claims


async def _load_document(document_id) -> Document:
    async with AsyncSessionLocal() as session:
        document = await session.get(Document, document_id)
    if document is None:
        raise ValueError(f"Document {document_id} not found")
    return document


async def _call_llm_and_parse(system: str, user_content) -> list[dict]:
    raw_text = await llm.complete(system, user_content)
    try:
        parsed = llm.parse_json_block(raw_text)
    except ValueError:
        # Re-prompt once, appending a format reminder.
        reminder = "Your previous reply was not valid JSON. Reply with ONLY the JSON array."
        if isinstance(user_content, str):
            retry_content = f"{user_content}\n\n{reminder}"
        else:
            retry_content = [*user_content, {"type": "text", "text": reminder}]
        raw_text = await llm.complete(system, retry_content)
        parsed = llm.parse_json_block(raw_text)
    if isinstance(parsed, dict):
        parsed = parsed.get("claims", [])
    return parsed if isinstance(parsed, list) else []


async def extract_claims(state: PipelineState) -> dict:
    if state.raw_claims:
        claims = _validate_claims([c.model_dump() for c in state.raw_claims])
        logger.info("extract_claims_passthrough", count=len(claims))
        return {"raw_claims": claims, "status": "extracted"}

    document = await _load_document(state.document_id)
    path = Path(document.storage_path)
    doc_type = document.doc_type

    if doc_type in (DocType.pdf_spec, DocType.web):
        if path.suffix.lower() == ".pdf":
            text = _extract_pdf_text(path)
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")
        user_content = build_extraction_user_prompt(text)
    else:
        image_data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
        user_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": _media_type_for(path),
                    "data": image_data,
                },
            },
            {"type": "text", "text": build_extraction_user_prompt(None)},
        ]

    raw_items = await _call_llm_and_parse(EXTRACTION_SYSTEM_PROMPT, user_content)
    claims = _validate_claims(raw_items)
    logger.info(
        "extract_claims_done", document_id=str(state.document_id), count=len(claims)
    )
    return {"raw_claims": claims, "status": "extracted"}
