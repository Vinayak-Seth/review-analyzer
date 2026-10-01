"""Web UI: streamlit run src/app.py"""

import pandas as pd
import streamlit as st

from analyzer import ReviewAnalyzer
from llm_client import LLMClient
from prompt_loader import PromptLoader
from report import build_markdown, compute_stats, generate_report


@st.cache_resource
def load_components():
    prompts = PromptLoader()
    client = LLMClient()
    return ReviewAnalyzer(client, prompts), client, prompts


st.title("Customer Review Analyzer")
analyzer, client, prompts = load_components()

mode = st.radio("Input", ["Single review", "Upload CSV"], horizontal=True)

if mode == "Single review":
    text = st.text_area("Paste a review")
    if st.button("Analyze") and text.strip():
        with st.spinner("Analyzing..."):
            st.json(analyzer.analyze_one(text))
else:
    file = st.file_uploader("CSV with a 'review' column", type="csv")
    if file and st.button("Analyze CSV"):
        with st.spinner("Analyzing reviews..."):
            results = analyzer.analyze_csv(file)
            stats = compute_stats(results)
            report = generate_report(results, client, prompts)
        st.dataframe(pd.DataFrame(results)[["id", "review", "sentiment", "summary"]])
        st.markdown(build_markdown(stats, report))