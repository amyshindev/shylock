from shylock_trial.app.utils.dialogue_text import (
    normalize_portia_names,
    sanitize_dialogue_line,
    sanitize_game_text,
)


def test_normalize_portia_names() -> None:
    assert normalize_portia_names("발타자르가 말했다") == "포샤가 말했다"
    assert normalize_portia_names("포르샤는") == "포샤는"
    assert normalize_portia_names("발타사르") == "포샤"


def test_sanitize_dialogue_line_strips_orphan_quote() -> None:
    line = '샤일록이 딸의 이름을 법정에 들고 나온 순간, 포샤는 눈 하나 깜짝하지 않았다. "'
    assert sanitize_dialogue_line(line).endswith("않았다.")
    assert '"' not in sanitize_dialogue_line(line)


def test_sanitize_dialogue_line_keeps_paired_quotes() -> None:
    line = '"기다리시오, 유대인."'
    assert sanitize_dialogue_line(line) == line


def test_sanitize_game_text() -> None:
    assert sanitize_game_text("  포르샤  ") == "포샤"
