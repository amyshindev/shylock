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

_SPEAKER_SUBJECTS = (
    r"그녀는|그가|그들은|"
    r"포샤는|포샤가|바사니오는|바사니오가|"
    r"재판장은|군중은|안토니오는|안토니오가|"
    r"샤일록은|샤일록이|투발은|투발이"
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


def _looks_like_narrative_prefix(before: str) -> bool:
    if re.search(r"[다한다았음]\.?\s*$", before):
        return True
    return bool(re.search(r"(?:가|이|는|을|를)\s+.+", before))


def _extract_embedded_quote(text: str) -> str | None:
    for open_q, close_q in _QUOTE_PAIRS + (('"', '"'),):
        start = text.find(open_q)
        if start == -1:
            continue
        end = text.rfind(close_q)
        if end <= start:
            continue

        before = text[:start].strip()
        inner = text[start + len(open_q) : end].strip()
        if not inner:
            continue
        if not before or _looks_like_narrative_prefix(before):
            return inner

    return None


def _strip_narrator_quote_tail(speech: str) -> str:
    """Remove trailing '고' left from '~노라고 그녀는 말했다' narrative wrappers."""
    return re.sub(r"(노라|하오|이오|리오)고$", r"\1", speech.strip())


def sanitize_character_direct_speech(text: str) -> str:
    """Strip third-person narration from character speech lines."""
    s = sanitize_dialogue_line(sanitize_game_text(text))
    if not s:
        return s

    embedded = _extract_embedded_quote(s)
    if embedded:
        return _strip_narrator_quote_tail(embedded)

    narrator_suffix = re.compile(
        rf"^(?P<speech>.+?)\s+(?:{_SPEAKER_SUBJECTS})\s*"
        r"(?:천천히\s+|차갑게\s+|조용히\s+|냉정히\s+)?"
        r"(?:말|선언|답|외치|일깨워|속삭|되물).*?$",
        re.DOTALL,
    )
    narrator_head = re.compile(
        rf"^(?:{_SPEAKER_SUBJECTS})\s*"
        r"(?:천천히\s+|차갑게\s+|조용히\s+|냉정히\s+)?"
        r"(?P<speech>.+?)(?:라고|하고)\s*(?:말|선언|답|외치).*?$",
        re.DOTALL,
    )

    for pattern in (narrator_suffix, narrator_head):
        match = pattern.match(s)
        if match:
            return _strip_narrator_quote_tail(match.group("speech").strip())

    return _strip_narrator_quote_tail(s)


def sanitize_portia_direct_speech(text: str) -> str:
    return sanitize_character_direct_speech(text)


def sanitize_game_text(text: str) -> str:
    return normalize_portia_names(text.strip())
