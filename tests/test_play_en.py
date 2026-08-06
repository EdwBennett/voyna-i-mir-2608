"""Tests for play_en.py, the English half of an English/Russian playback pair.

Uses the real bundled sentence-pair dataset for lookup and clause splitting,
but mocks say()/synthesize() so no audio is produced.
"""

from unittest.mock import MagicMock

import voyna_i_mir_2608.play.play_en as play_en_module

PAIR = play_en_module._load_pair(1)
FIRST_CLAUSE = "In the old house"


# -- _select_en_text -------------------------------------------------------------


def test_select_en_text_without_clause_returns_full_sentence():
    assert play_en_module._select_en_text(PAIR, None) == PAIR.en


def test_select_en_text_with_clause_returns_that_clause():
    assert play_en_module._select_en_text(PAIR, 1) == FIRST_CLAUSE


# -- _print_en ---------------------------------------------------------------------


def test_print_en_without_clause_prints_sentence_and_words(capsys):
    play_en_module._print_en(PAIR, None, PAIR.en)

    out = capsys.readouterr().out
    assert PAIR.en in out
    assert PAIR.words in out


def test_print_en_with_clause_prints_only_the_clause(capsys):
    play_en_module._print_en(PAIR, 1, FIRST_CLAUSE)

    out = capsys.readouterr().out
    assert FIRST_CLAUSE in out
    assert PAIR.words not in out


# -- play_en -----------------------------------------------------------------------


def test_play_en_speaks_full_sentence_when_no_clause(monkeypatch, capsys):
    mock_say = MagicMock()
    monkeypatch.setattr(play_en_module, "say", mock_say)

    play_en_module.play_en(1)()

    mock_say.assert_called_once_with(lang="en", text=PAIR.en)
    assert PAIR.en in capsys.readouterr().out


def test_play_en_speaks_only_the_given_clause(monkeypatch):
    mock_say = MagicMock()
    monkeypatch.setattr(play_en_module, "say", mock_say)

    play_en_module.play_en(1, clause=1)()

    mock_say.assert_called_once_with(lang="en", text=FIRST_CLAUSE)


# -- print_en ----------------------------------------------------------------------


def test_print_en_fn_prints_without_speaking(monkeypatch, capsys):
    mock_say = MagicMock()
    monkeypatch.setattr(play_en_module, "say", mock_say)

    play_en_module.print_en(1, clause=1)()

    mock_say.assert_not_called()
    assert FIRST_CLAUSE in capsys.readouterr().out


# -- render_en ---------------------------------------------------------------------


def test_render_en_returns_lead_in_silence_plus_synthesized_clause(monkeypatch):
    monkeypatch.setattr(
        play_en_module, "synthesize", lambda *, lang, text: f"AUDIO[{lang}]:{text}".encode()
    )

    audio = play_en_module.render_en(1, clause=1)

    expected_silence = play_en_module.silence(play_en_module.LEAD_IN_SECONDS)
    assert audio == expected_silence + f"AUDIO[en]:{FIRST_CLAUSE}".encode()
