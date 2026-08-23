from app.catalog.classify import classify_row


def test_classify_confident_match_with_embedding_candidates():
    candidates = [
        "Tools/Power Tools/Circular Saws",
        "Plumbing/Faucets/Kitchen",
        "Electrical/Wire/Copper",
    ]
    cp, conf = classify_row(
        "18V cordless circular saw kit with blade",
        "Milwaukee (4031)",
        candidates,
    )
    assert cp == "Tools/Power Tools/Circular Saws"
    assert conf >= 0.35


def test_classify_no_match_returns_honest_blank():
    candidates = ["Plumbing/Faucets/Kitchen", "Electrical/Wire/Copper"]
    cp, conf = classify_row("xyz123 unrelated gibberish", "Unknown Mfr", candidates)
    assert cp == ""
    assert conf == 0.0


def test_classify_fallback_heuristic_when_no_session():
    """Without a DB session the keyword-overlap tier handles classification."""
    candidates = ["Misc/General/Other", "HVAC/Air Filters/Pleated"]
    cp, conf = classify_row("HVAC pleated filter 16x25", "", candidates)
    assert cp == "HVAC/Air Filters/Pleated"
    assert conf >= 0.35


def test_classify_empty_candidates_is_blank():
    cp, conf = classify_row("some part", "Mfr", None)
    assert cp == ""
    assert conf == 0.0
