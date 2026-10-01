# Customer Review Analyzer

An NLP project that uses an LLM (Groq API) to analyze product reviews.
For each review it extracts sentiment, aspect-level sentiment, and a
one-line summary, then generates an overall report with pros, cons,
and recommendations.

## NLP tasks covered
- Sentiment analysis
- Aspect-based sentiment analysis
- Abstractive summarization
- Structured information extraction (JSON)

## Project structure
```
config/config.yaml      model, temperature, retries, file paths
prompts/prompts.yaml    all prompts (system, analysis, report)
src/llm_client.py       Groq API wrapper with retry + backoff
src/prompt_loader.py    loads and fills prompt templates
src/parser.py           cleans and validates LLM JSON output
src/analyzer.py         per-review and batch analysis
src/report.py           statistics + LLM-written report
src/main.py             command-line entry point
src/app.py              optional Streamlit UI
tests/test_parser.py    unit tests
```

## Setup
1. Clone the repo and open the folder.
2. Create and activate a virtual environment:
   `python -m venv venv` then `venv\Scripts\activate` (Windows)
   or `source venv/bin/activate` (Mac/Linux)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your Groq API key.

## Usage
```
python src/main.py                      # uses data/sample_reviews.csv
python src/main.py --input my_file.csv  # your own CSV (needs a 'review' column)
streamlit run src/app.py                # optional web UI
pytest                                  # run tests
```
Outputs: `outputs/results.json` and `outputs/report.md`.

## Design decisions
- **Prompts live in a separate YAML file**, so they can be changed without touching code.
- **Prompt techniques:** role-based system prompt, strict JSON schema, a one-shot example, and low temperature (0.2) for consistent output.
- **Robustness:** retries with exponential backoff, JSON cleanup and validation, and one failed review never stops the batch.
- **Efficiency:** counts and averages are computed in Python; the LLM is used only for analysis and for writing the report. The report prompt receives a compact version of the data.
- **Configurable:** model name, temperature, token limit, and paths are all in `config/config.yaml`.

## Example output

 Statistics
- Reviews analyzed: 5/5
- Failed: 0
- Sentiment counts: {'neutral': 2, 'negative': 1, 'positive': 2}
- Average confidence: 0.87

 AI Summary

 1. Overall Sentiment  
- **Balanced**: 2 positive, 2 neutral, 1 negative review.  
- The product is generally well‑received, with positive feedback outweighing the single negative comment.