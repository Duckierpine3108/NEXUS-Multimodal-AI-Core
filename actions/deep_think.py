# ==============================================================================
#                 ACTIONS: DEEP REASONING & THINKING AGENT
# ==============================================================================

import json
import os
from pathlib import Path
from google import genai
from google.genai import types

def _get_api_key() -> str:
    config_path = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
    try:
        return json.loads(config_path.read_text(encoding="utf-8")).get("gemini_api_key", "")
    except Exception:
        return ""

def _get_thinking_budget() -> int:
    config_path = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
    try:
        level = json.loads(config_path.read_text(encoding="utf-8")).get("thinking_level", "medium").lower()
        if level in ("low", "flash"):
            return 1024
        elif level == "high":
            return 8192
        else:
            return 4096
    except Exception:
        return 4096

def deep_think(parameters: dict, player=None, speak=None) -> str:
    """
    Executes deep reasoning using the latest active Gemini Thinking model
    with dynamic token budgets.
    """
    query = parameters.get("query", "")
    if not query:
        return "Please provide a query or problem to analyze."

    api_key = _get_api_key()
    if not api_key:
        return "Gemini API Key missing."

    budget = _get_thinking_budget()
    level_label = "HIGH (8K Budget)" if budget >= 8192 else ("LOW (1K Budget)" if budget <= 1024 else "MEDIUM (4K Budget)")

    if player and hasattr(player, "write_log"):
        player.write_log(f"SYS: ?? Deep Thinking [{level_label}] engaged...")

    try:
        client = genai.Client(api_key=api_key)

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=budget),
            system_instruction=(
                "You are an advanced analytical reasoning engine. "
                "Break down problems systematically, evaluate edge cases, "
                "verify logic thoroughly, and provide a clear, high-precision solution."
            )
        )

        candidate_models = [
            "gemini-2.5-flash",
            "gemini-flash-latest",
            "gemini-2.5-pro",
        ]

        response = None
        last_err = None

        for model_name in candidate_models:
            try:
                # 1. Try with deep thinking token budget
                response = client.models.generate_content(
                    model=model_name,
                    contents=query,
                    config=config,
                )
                if response and response.text:
                    break
            except Exception as err:
                last_err = err
                # 2. Fallback without thinking config if 503 busy
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=query,
                    )
                    if response and response.text:
                        break
                except Exception as inner_err:
                    last_err = inner_err
                    continue

        if response and response.text:
            result_text = response.text.strip()
            if player and hasattr(player, "show_content") and result_text:
                player.show_content(f"REASONING [{level_label}]", result_text)
            return result_text

        return f"Thinking engine failed: {last_err}"

    except Exception as e:
        return f"Thinking engine error: {e}"