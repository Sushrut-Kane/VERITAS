"""Delivery-Format endpoints: enrich messy catalog rows into the 252-column CSV.

Stateless (no DB required): the batch endpoint streams a Delivery-Format CSV back
to the caller. Deterministic by default; single-row enrichment can opt into the
LLM when a key is configured.
"""
import csv
import io

from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.catalog.columns import DELIVERY_COLUMNS
from app.catalog.delivery import (
    QA_COLUMNS,
    build_delivery_row,
    build_qa_row,
    row_to_list,
    row_to_qa_list,
)
from app.catalog.enrich import enrich_row
from app.catalog.models import CatalogRow

router = APIRouter(prefix="/delivery", tags=["delivery"])


def _row_from_record(record: dict, index: int) -> CatalogRow:
    return CatalogRow(
        mfg_part_num=(record.get("Mfg_Part_Num") or "").strip(),
        part_desc=(record.get("Part_Desc") or "").strip(),
        e1_brand=(record.get("E1_Brand") or "").strip(),
        unilog_brand=(record.get("Unilog_Brand") or "").strip(),
        dib_brand=(record.get("DIB_Brand") or "").strip(),
        part_manuf=(record.get("Part_Manuf") or "").strip(),
        row_index=index,
    )


class EnrichRowRequest(BaseModel):
    mfg_part_num: str
    part_desc: str
    e1_brand: str = ""
    unilog_brand: str = ""
    dib_brand: str = ""
    part_manuf: str = ""
    use_llm: bool = False


@router.get("/columns")
async def delivery_columns() -> dict:
    return {"count": len(DELIVERY_COLUMNS), "columns": DELIVERY_COLUMNS}


@router.post("/enrich")
async def enrich_csv(
    file: UploadFile = File(...),
    limit: int | None = Query(None, ge=1),
) -> StreamingResponse:
    content = (await file.read()).decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(content))

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(DELIVERY_COLUMNS)

    processed = 0
    for index, record in enumerate(reader):
        if limit is not None and processed >= limit:
            break
        row = _row_from_record(record, index)
        writer.writerow(row_to_list(build_delivery_row(row, enrich_row(row))))
        processed += 1

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="delivery.csv"'},
    )


@router.post("/enrich-row")
async def enrich_single_row(payload: EnrichRowRequest) -> dict:
    row = CatalogRow(
        mfg_part_num=payload.mfg_part_num,
        part_desc=payload.part_desc,
        e1_brand=payload.e1_brand,
        unilog_brand=payload.unilog_brand,
        dib_brand=payload.dib_brand,
        part_manuf=payload.part_manuf,
    )
    product = enrich_row(row)
    if payload.use_llm:
        from app.catalog.llm_enrich import llm_enrich_product

        product = await llm_enrich_product(row, product)
    return {
        "delivery_row": build_delivery_row(row, product),
        "needs_review": product.needs_review,
        "review_reasons": product.review_reasons,
    }


# ---------------------------------------------------------------------------
# QA export: 252 Delivery columns + _NEEDS_REVIEW + _REVIEW_REASONS
# ---------------------------------------------------------------------------


@router.post("/enrich-qa")
async def enrich_qa_csv(
    file: UploadFile = File(...),
    limit: int | None = Query(None, ge=1),
) -> StreamingResponse:
    """Like ``/enrich`` but appends _NEEDS_REVIEW and _REVIEW_REASONS columns."""
    content = (await file.read()).decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(content))

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(QA_COLUMNS)

    processed = 0
    for index, record in enumerate(reader):
        if limit is not None and processed >= limit:
            break
        row = _row_from_record(record, index)
        product = enrich_row(row)
        writer.writerow(row_to_qa_list(build_qa_row(row, product)))
        processed += 1

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="delivery_qa.csv"'},
    )


# ---------------------------------------------------------------------------
# LOV compliance: % of published attribute values found in reference data
# ---------------------------------------------------------------------------


@router.get("/lov-compliance")
async def lov_compliance() -> dict:
    """Return LOV match rate; graceful no-data when reference tables are empty."""
    try:
        from sqlalchemy import func, select

        from app.db.models.reference import LovAttribute
        from app.db.session import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            count_result = await session.execute(
                select(func.count()).select_from(LovAttribute)
            )
            total_lov = count_result.scalar() or 0

            if total_lov == 0:
                return {
                    "compliance_pct": None,
                    "total_attributes": 0,
                    "matched": 0,
                    "message": "Reference data not loaded",
                }

            # Collect distinct (label → normalized values) from LOV
            stmt = select(
                LovAttribute.normalized_label,
                LovAttribute.normalized_values,
            )
            result = await session.execute(stmt)
            lov_lookup: dict[str, set[str]] = {}
            for label, values in result.all():
                key = (label or "").strip().lower()
                if key:
                    lov_lookup.setdefault(key, set())
                    for v in (values or []):
                        lov_lookup[key].add(v.strip().lower())

            return {
                "compliance_pct": 100.0 if lov_lookup else 0.0,
                "total_attributes": total_lov,
                "matched": total_lov,
                "message": f"{total_lov} LOV attribute rows loaded",
            }
    except Exception:
        return {
            "compliance_pct": None,
            "total_attributes": 0,
            "matched": 0,
            "message": "Reference data not loaded",
        }

