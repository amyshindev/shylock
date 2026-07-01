import json
import re


from shylock_trial.app.utils.dialogue_text import sanitize_game_text


def extract_portia_text(raw: str) -> str:
    """Strip JSON wrappers when structured parsing returns raw JSON text."""
    trimmed = raw.strip()
    if not trimmed:
        return ""

    fence = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", trimmed, re.DOTALL | re.IGNORECASE)
    if fence:
        trimmed = fence.group(1).strip()

    if trimmed.startswith("{"):
        try:
            data = json.loads(trimmed)
            if isinstance(data, dict) and isinstance(data.get("text"), str):
                return sanitize_game_text(data["text"])
        except json.JSONDecodeError:
            match = re.search(
                r'"text"\s*:\s*"((?:[^"\\]|\\.)*)(?:"|$)',
                trimmed,
                re.DOTALL,
            )
            if match:
                try:
                    return sanitize_game_text(json.loads(f'"{match.group(1)}"'))
                except json.JSONDecodeError:
                    return sanitize_game_text(
                        match.group(1)
                        .replace("\\n", "\n")
                        .replace('\\"', '"')
                    )

    return sanitize_game_text(trimmed)
