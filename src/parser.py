"""Cleans and validates the JSON returned by the LLM."""

import json
import re

VALID_SENTIMENTS = {"positive", "negative", "neutral"}


def extract_json(raw: str) -> dict:
    """Pull a JSON object out of the model's reply, even if wrapped in extra text."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("No valid JSON found in model reply")


def validate_analysis(data: dict) -> dict:
    """Check required keys and fix small problems. Raises ValueError if unusable."""
    required = {"sentiment", "confidence", "aspects", "summary"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing keys: {missing}")

    sentiment = str(data["sentiment"]).lower().strip()
    if sentiment not in VALID_SENTIMENTS:
        raise ValueError(f"Invalid sentiment: {sentiment}")

    try:
        confidence = float(data["confidence"])
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = min(max(confidence, 0.0), 1.0)

    aspects = []
    for item in data["aspects"] or []:
        if isinstance(item, dict) and "aspect" in item and "sentiment" in item:
            aspects.append(
                {
                    "aspect": str(item["aspect"]).lower().strip(),
                    "sentiment": str(item["sentiment"]).lower().strip(),
                }
            )

    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "aspects": aspects,
        "summary": str(data["summary"]).strip(),
    }


def parse_response(raw: str) -> dict:
    """Extract and validate in one call."""
    return validate_analysis(extract_json(raw))