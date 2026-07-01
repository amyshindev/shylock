import re

_PORTIA_NAME_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"발타사르"), "포샤"),
    (re.compile(r"발타자(?:르|사)?"), "포샤"),
    (re.compile(r"포르샤"), "포샤"),
    (re.compile(r"Balthazar", re.IGNORECASE), "포샤"),
)

_QUOTE_PAIRS = (
    ('"', '"'),
    ('"', '"'),
    ("「", "」"),
    ("『", "』"),
)


def normalize_portia_names(text: str) -> str:
    normalized = text
    for pattern, replacement in _PORTIA_NAME_PATTERNS:
        normalized = pattern.sub(replacement, normalized)
    return normalized


def sanitize_dialogue_line(line: str) -> str:
    s = normalize_portia_names(line.strip())
    if not s:
        return s

    if s.count('"') == 1:
        if s.startswith('"'):
            s = s[1:].lstrip()
        elif s.endswith('"'):
            s = s[:-1].rstrip()

    for open_q, close_q in _QUOTE_PAIRS:
        opens = s.count(open_q)
        closes = s.count(close_q)
        if opens == closes:
            continue
        if closes > opens and s.endswith(close_q):
            s = s[: -len(close_q)].rstrip()
        if opens > closes and s.startswith(open_q):
            s = s[len(open_q) :].lstrip()

    return s.strip()


def sanitize_game_text(text: str) -> str:
    return normalize_portia_names(text.strip())
