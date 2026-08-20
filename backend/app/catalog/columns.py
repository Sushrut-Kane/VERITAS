"""Canonical column lists for the UniLog Delivery Format.

The 252 column names (and their order) are the frozen contract judges score
against. The repeated groups (ITEM_FEATURES 1..20, ATTRIBUTE_* 1..50) are
generated programmatically so they can never drift or be mistyped.
"""

INPUT_COLUMNS = [
    "Mfg_Part_Num",
    "Part_Desc",
    "E1_Brand",
    "Unilog_Brand",
    "DIB_Brand",
    "Part_Manuf",
]

MAX_ATTRIBUTES = 50
MAX_ITEM_FEATURES = 20

_HEAD = [
    "MFR URL",
    "Ref URL 1",
    "Ref URL 2",
    "Ref URL 3",
    "Ref URL 4",
    "Ref URL 5",
    "PART_NUMBER",
    "Dept",
    "Class",
    "Fine",
    "SKU - MY_PART_NUMBER",
    "Mfg_Part_Num",
    "Part_Desc",
    "E1_Brand",
    "Unilog_Brand",
    "DIB_Brand",
    "Part_Manuf",
    "MANUFACTURER_NAME",
    "BRAND_NAME",
    "TRADE_NAME",
    "MANUFACTURER_PART_NUMBER",
    "ALTERNATE_PART_NUMBER",
    "Classpath",
    "MOBILE_DESC",
    "INVOICE_DESC",
    "SHORT_DESC",
    "LONG_DESC1",
    "RETAIL_DESC",
    "MARKETING_DESCRIPTION",
]

_ITEM_FEATURES = [f"ITEM_FEATURES_{i}" for i in range(1, MAX_ITEM_FEATURES + 1)]

_MID = [
    "With",
    "Standard/Approvals",
    "Prop 65",
    "Application",
    "Includes",
    "Product Name",
]


def _attribute_triplet_columns() -> list[str]:
    cols: list[str] = []
    for i in range(1, MAX_ATTRIBUTES + 1):
        cols += [f"ATTRIBUTE_LABEL {i}", f"ATTRIBUTE_VALUE {i}", f"ATTRIBUTE_UOM {i}"]
    return cols


_TAIL = [
    "UPC",
    "EAN",
    "GTIN",
    "UNSPSC",
    "Warranty",
    "List Price",
    "Selling Qty",
    "Selling UOM",
    "Standard Packaging Information",
    "LENGTH",
    "LENGTH_UOM",
    "HEIGHT",
    "HEIGHT_UOM",
    "WIDTH",
    "WIDTH_UOM",
    "WEIGHT",
    "WEIGHT_UOM",
    "VOLUME",
    "VOLUME_UOM",
    "Product Image",
    "Alternate Image 1",
    "Alternate Image 2",
    "Alternate Image 3",
    "Alternate Image 4",
    "SDS",
    "SDS_1",
    "Warranty Information",
    "Catalog",
    "Specification Sheet",
    "Instruction/Installation Manual",
    "Service Manual",
    "Owners/User Manual",
    "Line Drawing",
    "MTR",
    "RoHS",
    "Full Engineering Drawing",
    "Energy Star Guide",
    "Technical Bulletin",
    "Submittal",
    "Compatibility Chart",
    "Size Chart",
    "Product Label/Insert",
    "Video Link",
    "Video Link 1",
    "Country Of Origin",
    "Discontinued",
    "Actual Image (Yes/No)",
]

DELIVERY_COLUMNS: list[str] = (
    _HEAD + _ITEM_FEATURES + _MID + _attribute_triplet_columns() + _TAIL
)

# The delivery template is a frozen 252-column contract; fail loudly if edited.
assert len(DELIVERY_COLUMNS) == 252, (
    f"Delivery template must have 252 columns, got {len(DELIVERY_COLUMNS)}"
)
