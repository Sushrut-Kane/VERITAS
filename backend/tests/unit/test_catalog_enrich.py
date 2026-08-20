from app.catalog.columns import DELIVERY_COLUMNS
from app.catalog.delivery import build_delivery_row
from app.catalog.enrich import enrich_row
from app.catalog.models import CatalogRow


def test_enrich_row_parses_manufacturer_and_dimensions():
    row = CatalogRow(
        mfg_part_num="49-94-0053",
        part_desc='49-94-0053 Milw 12"x1/8"x1" Metal Cut Off Disc',
        e1_brand="-- Unbranded --",
        unilog_brand="-- No Unilog Brand --",
        dib_brand="-- No DIB Brand --",
        part_manuf="Milwaukee Accessory (4031)",
    )
    product = enrich_row(row)

    assert product.manufacturer_name == "Milwaukee Accessory"
    assert product.manufacturer_code == "4031"
    assert product.brand_name == ""  # every input brand was a placeholder
    assert any(a.label == "Diameter" and a.value == "12" for a in product.attributes)
    # "Milw" abbreviation matches the manufacturer, so it is stripped from the type.
    assert not product.product_type.lower().startswith("milw ")


def test_build_delivery_row_has_full_column_set():
    row = CatalogRow(
        mfg_part_num="A1", part_desc='A1 Something 5" Disc', part_manuf="Foo (9)"
    )
    data = build_delivery_row(row, enrich_row(row))

    assert set(data.keys()) == set(DELIVERY_COLUMNS)
    assert data["Mfg_Part_Num"] == "A1"
    assert data["MANUFACTURER_NAME"] == "Foo"
    assert data["PART_NUMBER"] == "A1"
    assert data["ATTRIBUTE_LABEL 1"]  # at least one attribute emitted


def test_brand_manufacturer_mismatch_flags_review():
    row = CatalogRow(
        mfg_part_num="D1",
        part_desc="D1 Dishwasher",
        unilog_brand="FRIGIDAIRE",
        part_manuf="Rheem Manufacturing (RHEEM)",
    )
    product = enrich_row(row)
    assert product.needs_review is True
    assert product.review_reasons
