from app.catalog.descriptions import build_all
from app.catalog.models import Attribute, EnrichedProduct


def _product() -> EnrichedProduct:
    return EnrichedProduct(
        part_number="X1",
        part_desc="desc",
        manufacturer_name="Acme Co",
        brand_name="Acme",
        product_type="Metal Cut Off Disc",
        attributes=[
            Attribute("Diameter", "12", "in"),
            Attribute("Thickness", "1/8", "in"),
            Attribute("Grit", "P80"),
            Attribute("Type", "Metal Cut Off Disc"),
        ],
    )


def test_invoice_desc_is_uppercase_and_within_40():
    product = build_all(_product())
    assert product.invoice_desc == product.invoice_desc.upper()
    assert len(product.invoice_desc) <= 40


def test_mobile_desc_within_80():
    product = build_all(_product())
    assert len(product.mobile_desc) <= 80


def test_type_attribute_excluded_from_rollup():
    product = build_all(_product())
    # product_type appears once (as the head), not repeated as an attribute phrase.
    assert product.retail_desc.count("Metal Cut Off Disc") == 1


def test_descriptions_nonempty_and_product_name():
    product = build_all(_product())
    assert product.short_desc
    assert product.long_desc
    assert product.retail_desc
    assert product.product_name == "Metal Cut Off Disc"
