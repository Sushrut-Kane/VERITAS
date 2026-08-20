from app.catalog.fractions import decimal_to_inch_fraction as d2f
from app.catalog.fractions import inch_fraction_to_decimal as f2d
from app.catalog.uom import canonical_uom, format_quantity


def test_mixed_fraction_to_decimal():
    assert f2d("50-1/4") == 50.25


def test_simple_fraction_to_decimal():
    assert f2d("1/2") == 0.5


def test_whole_number_to_decimal():
    assert f2d("3") == 3.0


def test_fraction_with_quote():
    assert f2d('7/8"') == 0.875


def test_decimal_to_fraction():
    assert d2f(50.25) == "50-1/4"
    assert d2f(0.5) == "1/2"
    assert d2f(1.0) == "1"


def test_fraction_roundtrip():
    assert d2f(f2d("50-1/4")) == "50-1/4"


def test_canonical_uom():
    assert canonical_uom("inches") == "in"
    assert canonical_uom('"') == "in"
    assert canonical_uom("volts") == "V"


def test_format_quantity_spacing():
    assert format_quantity("120", "volts") == "120 V"
    assert format_quantity("5", "") == "5"
