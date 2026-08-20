"""Plain dataclasses shared across the catalog layer (stdlib only)."""
from dataclasses import dataclass, field


@dataclass
class CatalogRow:
    mfg_part_num: str
    part_desc: str
    e1_brand: str = ""
    unilog_brand: str = ""
    dib_brand: str = ""
    part_manuf: str = ""
    row_index: int = 0


@dataclass
class Attribute:
    label: str
    value: str
    uom: str = ""


@dataclass
class EnrichedProduct:
    part_number: str
    part_desc: str
    manufacturer_name: str = ""
    manufacturer_code: str = ""
    brand_name: str = ""
    product_type: str = ""
    series: str = ""
    classpath: str = ""
    attributes: list[Attribute] = field(default_factory=list)
    item_features: list[str] = field(default_factory=list)
    invoice_desc: str = ""
    mobile_desc: str = ""
    short_desc: str = ""
    long_desc: str = ""
    retail_desc: str = ""
    marketing_desc: str = ""
    product_name: str = ""
    needs_review: bool = False
    review_reasons: list[str] = field(default_factory=list)
