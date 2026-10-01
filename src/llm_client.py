"""Wrapper around the Groq API with retries and error handling."""

import logging
import os
import time

import yaml
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
logger = logging.getLogger(__name__)


class LLMClient:
    """Sends prompts to Groq and returns the text reply."""

    def __init__(self, config_path: str = "config/config.yaml") -> None:
        with open(config_path, encoding="utf-8") as f:
            self.cfg: dict = yaml.safe_load(f)["llm"]

        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("API_KEY not found. Add it to your .env file.")

        self.client = Groq(api_key=api_key)

    def generate(self, user_prompt: str, system_prompt: str = "") -> str:
        """Call the LLM and return its reply. Retries with backoff on failure."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        max_retries = self.cfg["max_retries"]
        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.cfg["model"],
                    messages=messages,
                    temperature=self.cfg["temperature"],
                    max_tokens=self.cfg["max_tokens"],
                )
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Model returned an empty reply")
                return content.strip()
            except Exception as e:
                logger.warning("Attempt %d/%d failed: %s", attempt, max_retries, e)
                if attempt == max_retries:
                    raise RuntimeError(
                        f"LLM call failed after {max_retries} attempts: {e}"
                    ) from e
                time.sleep(2 ** attempt)  # wait 2s, 4s, 8s...