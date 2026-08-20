from app.catalog.columns import DELIVERY_COLUMNS, INPUT_COLUMNS


def test_delivery_has_252_columns():
    assert len(DELIVERY_COLUMNS) == 252


def test_no_duplicate_columns():
    assert len(set(DELIVERY_COLUMNS)) == 252


def test_key_columns_in_expected_positions():
    assert DELIVERY_COLUMNS[0] == "MFR URL"
    assert DELIVERY_COLUMNS[11] == "Mfg_Part_Num"
    assert DELIVERY_COLUMNS[22] == "Classpath"
    assert DELIVERY_COLUMNS[-1] == "Actual Image (Yes/No)"


def test_attribute_triplets_present():
    assert "ATTRIBUTE_LABEL 1" in DELIVERY_COLUMNS
    assert "ATTRIBUTE_VALUE 1" in DELIVERY_COLUMNS
    assert "ATTRIBUTE_UOM 50" in DELIVERY_COLUMNS


def test_input_columns():
    assert INPUT_COLUMNS[0] == "Mfg_Part_Num"
    assert "Part_Manuf" in INPUT_COLUMNS
