"""Core logic: analyzes each review using the LLM."""

import logging

import pandas as pd

from llm_client import LLMClient
from parser import parse_response
from prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class ReviewAnalyzer:
    """Runs sentiment, aspect, and summary analysis on reviews."""

    def __init__(self, client: LLMClient, prompts: PromptLoader) -> None:
        self.client = client
        self.prompts = prompts
        self.system_prompt = prompts.get("system")

    def analyze_one(self, review_text: str) -> dict:
        """Analyze a single review. Returns a result dict, never crashes."""
        review_text = review_text.strip()
        prompt = self.prompts.get("review_analysis", review_text=review_text)
        try:
            raw = self.client.generate(prompt, system_prompt=self.system_prompt)
            result = parse_response(raw)
            result["error"] = None
        except Exception as e:
            logger.error("Failed to analyze review: %s", e)
            result = {
                "sentiment": None,
                "confidence": 0.0,
                "aspects": [],
                "summary": "",
                "error": str(e),
            }
        result["review"] = review_text
        return result

    def analyze_csv(self, csv_path: str) -> list[dict]:
        """Analyze every review in a CSV file (needs 'id' and 'review' columns)."""
        df = pd.read_csv(csv_path)
        if "review" not in df.columns:
            raise ValueError("CSV must have a 'review' column")

        df = df.dropna(subset=["review"])
        if df.empty:
            raise ValueError("CSV contains no reviews")

        results = []
        total = len(df)
        for i, row in enumerate(df.itertuples(index=False), start=1):
            print(f"Analyzing review {i}/{total}...")
            result = self.analyze_one(str(row.review))
            result["id"] = getattr(row, "id", i)
            results.append(result)
        return results