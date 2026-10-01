"""Entry point: python src/main.py"""

import argparse
import json
import logging
import os

import yaml

from analyzer import ReviewAnalyzer
from llm_client import LLMClient
from prompt_loader import PromptLoader
from report import build_markdown, compute_stats, generate_report


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Customer Review Analyzer")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--input", help="CSV file (overrides config)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    cfg = load_config(args.config)
    paths = cfg["paths"]
    input_path = args.input or paths["input"]

    prompts = PromptLoader(paths["prompts"])
    client = LLMClient(args.config)
    analyzer = ReviewAnalyzer(client, prompts)

    # 1. Analyze every review
    results = analyzer.analyze_csv(input_path)

    # 2. Save raw results
    for p in (paths["output"], paths["report"]):
        os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(paths["output"], "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 3. Build and save the report
    print("Generating report...")
    stats = compute_stats(results)
    report_text = build_markdown(stats, generate_report(results, client, prompts))
    with open(paths["report"], "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"\nDone. Results: {paths['output']} | Report: {paths['report']}")
    print(f"Sentiments: {stats['sentiments']}")


if __name__ == "__main__":
    main()