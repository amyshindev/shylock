from shylock_trial.app.utils.dialogue_text import (
    normalize_portia_names,
    sanitize_character_direct_speech,
    sanitize_dialogue_line,
    sanitize_game_text,
    sanitize_portia_direct_speech,
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


def test_sanitize_portia_direct_speech_strips_narrator_tail() -> None:
    raw = (
        "인간임을 말하는 것은 쉬우나, 법정은 말이 아니라 증서와 법조문 위에 서 있노라고 "
        "그녀는 천천히 선언하였다."
    )
    assert sanitize_portia_direct_speech(raw) == (
        "인간임을 말하는 것은 쉬우나, 법정은 말이 아니라 증서와 법조문 위에 서 있노라"
    )


def test_sanitize_portia_direct_speech_keeps_direct_speech() -> None:
    line = "법정은 말이 아니라 증서와 법조문 위에 서 있노라."
    assert sanitize_portia_direct_speech(line) == line


def test_sanitize_character_direct_speech_strips_bassanio_narration() -> None:
    raw = (
        '바사니오가 앞으로 나서며 목소리를 높인다. '
        '"샤일록, 원금의 열 배를 내놓겠소. 그 돈을 받으시오."'
    )
    assert sanitize_character_direct_speech(raw) == (
        "샤일록, 원금의 열 배를 내놓겠소. 그 돈을 받으시오."
    )
