import json
import re


def extract_portia_text(raw: str) -> str:
    """Strip JSON wrappers when structured parsing returns raw JSON text."""
    trimmed = raw.strip()
    if not trimmed:
        return ""

    if trimmed.startswith("{"):
        try:
            data = json.loads(trimmed)
            if isinstance(data, dict) and isinstance(data.get("text"), str):
                return data["text"].strip()
        except json.JSONDecodeError:
            match = re.search(
                r'"text"\s*:\s*"((?:[^"\\]|\\.)*)(?:"|$)',
                trimmed,
                re.DOTALL,
            )
            if match:
                try:
                    return json.loads(f'"{match.group(1)}"')
                except json.JSONDecodeError:
                    return (
                        match.group(1)
                        .replace("\\n", "\n")
                        .replace('\\"', '"')
                        .strip()
                    )

    return trimmed
