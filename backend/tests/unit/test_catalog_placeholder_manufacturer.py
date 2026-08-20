from app.catalog.manufacturer import parse_manufacturer
from app.catalog.placeholder import clean_brand, first_real_brand, is_placeholder


def test_known_placeholders_are_detected():
    for value in [
        "-- Unbranded --",
        "-- No Unilog Brand --",
        "-- No DIB Brand --",
        "",
        None,
    ]:
        assert is_placeholder(value)


def test_real_brand_is_not_placeholder():
    assert not is_placeholder("3M")


def test_clean_brand():
    assert clean_brand("-- Unbranded --") == ""
    assert clean_brand("  Milwaukee ") == "Milwaukee"


def test_first_real_brand_picks_first_non_placeholder():
    assert first_real_brand("-- Unbranded --", "-- No Unilog Brand --", "3M") == "3M"
    assert first_real_brand("-- Unbranded --") == ""


def test_parse_manufacturer_with_code():
    assert parse_manufacturer("Freud Inc (2435)") == ("Freud Inc", "2435")
    assert parse_manufacturer("Milwaukee Accessory (4031)") == (
        "Milwaukee Accessory",
        "4031",
    )


def test_parse_manufacturer_without_code():
    assert parse_manufacturer("3 M Co") == ("3 M Co", "")


def test_parse_manufacturer_empty():
    assert parse_manufacturer("") == ("", "")
    assert parse_manufacturer(None) == ("", "")
