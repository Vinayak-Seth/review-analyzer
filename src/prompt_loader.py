"""Loads prompt templates from YAML and fills in their variables."""

import yaml


class PromptLoader:
    """Reads prompts.yaml once and returns formatted prompts by name."""

    def __init__(self, path: str = "prompts/prompts.yaml") -> None:
        with open(path, encoding="utf-8") as f:
            self.prompts: dict[str, str] = yaml.safe_load(f)

    def get(self, name: str, **variables: str) -> str:
        """Return the prompt called `name` with {placeholders} replaced."""
        if name not in self.prompts:
            raise KeyError(f"Prompt '{name}' not found in prompts file")
        text = self.prompts[name]
        for key, value in variables.items():
            text = text.replace("{" + key + "}", str(value))
        return text.strip()