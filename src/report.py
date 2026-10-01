"""Builds the final summary report from analyzed reviews."""

import json
from collections import Counter

from llm_client import LLMClient
from prompt_loader import PromptLoader


def compute_stats(results: list[dict]) -> dict:
    """Calculate counts and averages locally (no LLM call needed)."""
    ok = [r for r in results if r["error"] is None]
    sentiment_counts = Counter(r["sentiment"] for r in ok)
    aspect_counts: Counter = Counter()
    for r in ok:
        for a in r["aspects"]:
            aspect_counts[(a["aspect"], a["sentiment"])] += 1

    avg_conf = sum(r["confidence"] for r in ok) / len(ok) if ok else 0.0
    return {
        "total": len(results),
        "analyzed": len(ok),
        "failed": len(results) - len(ok),
        "sentiments": dict(sentiment_counts),
        "avg_confidence": round(avg_conf, 2),
        "top_aspects": aspect_counts.most_common(5),
    }


def generate_report(
    results: list[dict], client: LLMClient, prompts: PromptLoader
) -> str:
    """Ask the LLM to write the pros/cons/recommendations section."""
    ok = [r for r in results if r["error"] is None]
    if not ok:
        raise ValueError("No successfully analyzed reviews to report on")

    # Send only the useful fields, which keeps the prompt short and cheap
    compact = [
        {"sentiment": r["sentiment"], "aspects": r["aspects"], "summary": r["summary"]}
        for r in ok
    ]
    prompt = prompts.get("final_report", analysis_json=json.dumps(compact))
    return client.generate(prompt, system_prompt=prompts.get("report_system"))


def build_markdown(stats: dict, llm_text: str) -> str:
    """Combine the calculated stats and the LLM text into one report."""
    lines = [
        "# Customer Review Analysis Report",
        "",
        "## Statistics",
        f"- Reviews analyzed: {stats['analyzed']}/{stats['total']}",
        f"- Failed: {stats['failed']}",
        f"- Sentiment counts: {stats['sentiments']}",
        f"- Average confidence: {stats['avg_confidence']}",
        "",
        "## Most mentioned aspects",
    ]
    for (aspect, sentiment), count in stats["top_aspects"]:
        lines.append(f"- {aspect} ({sentiment}): {count}")
    lines += ["", "## AI Summary", "", llm_text]
    return "\n".join(lines)