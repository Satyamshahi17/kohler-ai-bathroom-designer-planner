from app.llm.requirements import parse_basic_requirements


def test_basic_requirement_fallback_extracts_explicit_constraints():
    result = parse_basic_requirements(
        "I want a warm Japanese Zen bathroom under $5000 with a wall-mounted vanity, toilet and shower."
    )
    assert result.budget == 5000
    assert result.theme == "Japanese Zen"
    assert set(result.required_categories) == {"vanity", "toilet", "shower"}
    assert "warm" in result.preferences
    assert "wall-mounted" in result.preferences
