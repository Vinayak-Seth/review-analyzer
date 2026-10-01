import pytest

from parser import extract_json, parse_response, validate_analysis

GOOD = {
    "sentiment": "positive",
    "confidence": 0.9,
    "aspects": [{"aspect": "Battery", "sentiment": "positive"}],
    "summary": "Great battery.",
}


def test_extract_plain_json():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_markdown_fence():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_extract_with_extra_text():
    assert extract_json('Here you go: {"a": 1} Hope it helps') == {"a": 1}


def test_no_json_raises():
    with pytest.raises(ValueError):
        extract_json("no json here")


def test_validate_clamps_confidence():
    data = {**GOOD, "confidence": 1.7}
    assert validate_analysis(data)["confidence"] == 1.0


def test_validate_normalizes_aspects():
    assert validate_analysis(GOOD)["aspects"][0]["aspect"] == "battery"


def test_invalid_sentiment_raises():
    with pytest.raises(ValueError):
        validate_analysis({**GOOD, "sentiment": "happy"})


def test_missing_keys_raises():
    with pytest.raises(ValueError):
        validate_analysis({"sentiment": "positive"})


def test_parse_response_end_to_end():
    raw = '```json\n{"sentiment":"negative","confidence":0.7,"aspects":[],"summary":"Bad."}\n```'
    assert parse_response(raw)["sentiment"] == "negative"