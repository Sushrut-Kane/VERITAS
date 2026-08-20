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
from app.catalog.delivery import build_delivery_row, row_to_list
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
