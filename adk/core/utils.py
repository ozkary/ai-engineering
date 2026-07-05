# core/utils.py
import os


def load_prompt_asset(file_name: str) -> str:
    """Reads a static prompt asset from the core prompts directory."""
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "prompts", file_name)

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()
