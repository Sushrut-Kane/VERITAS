from app.catalog.desc_parser import parse_part_desc


def _labels(attrs):
    return {a.label: (a.value, a.uom) for a in attrs}


def test_disc_three_dimensions():
    attrs, product_type = parse_part_desc(
        '49-94-0053 Milw 12"x1/8"x1" Metal Cut Off Disc', "49-94-0053"
    )
    labels = _labels(attrs)
    assert labels["Diameter"] == ("12", "in")
    assert labels["Thickness"] == ("1/8", "in")
    assert labels["Arbor Size"] == ("1", "in")
    assert "Metal Cut Off Disc" in product_type


def test_grit_and_pack_extracted():
    attrs, _ = parse_part_desc(
        "3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box", ""
    )
    labels = _labels(attrs)
    assert labels["Grit"][0] == "P150"
    assert labels["Package Quantity"][0] == "50"


def test_two_dimensions_width_length():
    attrs, _ = parse_part_desc(
        'DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc', "DCB518ASTS06G"
    )
    labels = _labels(attrs)
    assert labels["Width"] == ("1/2", "in")
    assert labels["Length"] == ("18", "in")


def test_decimal_thickness():
    attrs, _ = parse_part_desc('49-94-0001 Milw 4"x.040"x5/8" Metal Cut Off Disc', "49-94-0001")
    labels = _labels(attrs)
    assert labels["Diameter"] == ("4", "in")
    assert labels["Thickness"] == (".040", "in")
    assert labels["Arbor Size"] == ("5/8", "in")
