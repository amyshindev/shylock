import json


def serialize_string_tuple(values: tuple[str, ...]) -> str | None:
    if not values:
        return None
    return json.dumps(list(values), ensure_ascii=False)


def deserialize_string_tuple(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return ()
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        return ()
    return tuple(str(item) for item in parsed)


def append_unique(values: tuple[str, ...], value: str) -> tuple[str, ...]:
    if value in values:
        return values
    return (*values, value)
