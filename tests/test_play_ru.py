"""Tests for play_ru.py, the Russian half of an English/Russian playback pair.

Uses the real bundled sentence-pair dataset for lookup and clause splitting,
but mocks say()/synthesize() so no audio is produced.
"""

from unittest.mock import MagicMock

import voyna_i_mir_2608.play.play_ru as play_ru_module

PAIR = play_ru_module._load_pair(1)
FIRST_CLAUSE = "В старом доме"


# -- _select_ru_text -------------------------------------------------------------


def test_select_ru_text_without_clause_returns_full_sentence():
    assert play_ru_module._select_ru_text(PAIR, None) == PAIR.ru


def test_select_ru_text_with_clause_returns_that_clause():
    assert play_ru_module._select_ru_text(PAIR, 1) == FIRST_CLAUSE


# -- _print_ru ---------------------------------------------------------------------


def test_print_ru_without_clause_prints_sentence_and_ipa(capsys):
    play_ru_module._print_ru(PAIR, None, PAIR.ru)

    out = capsys.readouterr().out
    assert PAIR.ru in out
    assert PAIR.ipa in out


def test_print_ru_with_clause_prints_only_the_clause_and_ipa(capsys):
    play_ru_module._print_ru(PAIR, 1, FIRST_CLAUSE)

    out = capsys.readouterr().out
    assert FIRST_CLAUSE in out
    assert PAIR.ipa in out
    assert PAIR.ru not in out


# -- play_ru -----------------------------------------------------------------------


def test_play_ru_speaks_full_sentence_when_no_clause(monkeypatch, capsys):
    mock_say = MagicMock()
    monkeypatch.setattr(play_ru_module, "say", mock_say)

    play_ru_module.play_ru(1)()

    mock_say.assert_called_once_with(lang="ru", text=PAIR.ru)
    assert PAIR.ru in capsys.readouterr().out


def test_play_ru_speaks_only_the_given_clause(monkeypatch):
    mock_say = MagicMock()
    monkeypatch.setattr(play_ru_module, "say", mock_say)

    play_ru_module.play_ru(1, clause=1)()

    mock_say.assert_called_once_with(lang="ru", text=FIRST_CLAUSE)


# -- print_ru ----------------------------------------------------------------------


def test_print_ru_fn_prints_without_speaking(monkeypatch, capsys):
    mock_say = MagicMock()
    monkeypatch.setattr(play_ru_module, "say", mock_say)

    play_ru_module.print_ru(1, clause=1)()

    mock_say.assert_not_called()
    assert FIRST_CLAUSE in capsys.readouterr().out


# -- render_ru ---------------------------------------------------------------------


def test_render_ru_returns_lead_in_silence_plus_synthesized_clause(monkeypatch):
    monkeypatch.setattr(
        play_ru_module, "synthesize", lambda *, lang, text: f"AUDIO[{lang}]:{text}".encode()
    )

    audio = play_ru_module.render_ru(1, clause=1)

    expected_silence = play_ru_module.silence(play_ru_module.LEAD_IN_SECONDS)
    assert audio == expected_silence + f"AUDIO[ru]:{FIRST_CLAUSE}".encode()
