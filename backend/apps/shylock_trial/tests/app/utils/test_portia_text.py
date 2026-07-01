import json

import pytest

from shylock_trial.app.utils.portia_text import extract_portia_text


def test_extract_plain_text():
    assert extract_portia_text("법정은 침묵한다.") == "법정은 침묵한다."


def test_extract_json_object():
    raw = '{"text": "그렇다면 베니스에는 힘없다."}'
    assert extract_portia_text(raw) == "그렇다면 베니스에는 힘없다."


def test_extract_markdown_json_fence():
    raw = '```json\n{"text": "법정은 고요하다."}\n```'
    assert extract_portia_text(raw) == "법정은 고요하다."


def test_extract_truncated_json():
    raw = '{"text": "계약은 유효하며, 법정은'
    assert extract_portia_text(raw).startswith("계약은 유효하며")
