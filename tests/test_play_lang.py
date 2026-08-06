"""Tests for play_lang.py, the English and Russian halves of a playback pair.

Uses the real bundled sentence-pair dataset for lookup and clause splitting,
but mocks say()/synthesize() so no audio is produced.
"""

from unittest.mock import MagicMock

import voyna_i_mir_2608.play.play_lang as play_lang_module

PAIR = play_lang_module._load_pair(1)
FIRST_CLAUSE_EN = "In the old house"
FIRST_CLAUSE_RU = "В старом доме"


# -- _select_en_text -------------------------------------------------------------


def test_select_en_text_without_clause_returns_full_sentence():
    assert play_lang_module._select_en_text(PAIR, None) == PAIR.en


def test_select_en_text_with_clause_returns_that_clause():
    assert play_lang_module._select_en_text(PAIR, 1) == FIRST_CLAUSE_EN


# -- _select_ru_text -------------------------------------------------------------


def test_select_ru_text_without_clause_returns_full_sentence():
    assert play_lang_module._select_ru_text(PAIR, None) == PAIR.ru


def test_select_ru_text_with_clause_returns_that_clause():
    assert play_lang_module._select_ru_text(PAIR, 1) == FIRST_CLAUSE_RU


# -- _print_en ---------------------------------------------------------------------


def test_print_en_without_clause_prints_sentence_and_words(capsys):
    play_lang_module._print_en(PAIR, None, PAIR.en)

    out = capsys.readouterr().out
    assert PAIR.en in out
    assert PAIR.words in out


def test_print_en_with_clause_prints_only_the_clause(capsys):
    play_lang_module._print_en(PAIR, 1, FIRST_CLAUSE_EN)

    out = capsys.readouterr().out
    assert FIRST_CLAUSE_EN in out
    assert PAIR.words not in out


# -- _print_ru ---------------------------------------------------------------------


def test_print_ru_without_clause_prints_sentence_and_ipa(capsys):
    play_lang_module._print_ru(PAIR, None, PAIR.ru)

    out = capsys.readouterr().out
    assert PAIR.ru in out
    assert PAIR.ipa in out


def test_print_ru_with_clause_prints_only_the_clause_and_ipa(capsys):
    play_lang_module._print_ru(PAIR, 1, FIRST_CLAUSE_RU)

    out = capsys.readouterr().out
    assert FIRST_CLAUSE_RU in out
    assert PAIR.ipa in out
    assert PAIR.ru not in out


# -- play_en -----------------------------------------------------------------------


def test_play_en_speaks_full_sentence_when_no_clause(monkeypatch, capsys):
    mock_say = MagicMock()
    monkeypatch.setattr(play_lang_module, "say", mock_say)

    play_lang_module.play_en(1)()

    mock_say.assert_called_once_with(lang="en", text=PAIR.en, voice=None)
    assert PAIR.en in capsys.readouterr().out


def test_play_en_speaks_only_the_given_clause(monkeypatch):
    mock_say = MagicMock()
    monkeypatch.setattr(play_lang_module, "say", mock_say)

    play_lang_module.play_en(1, clause=1)()

    mock_say.assert_called_once_with(lang="en", text=FIRST_CLAUSE_EN, voice=None)


# -- play_ru -----------------------------------------------------------------------


def test_play_ru_speaks_full_sentence_when_no_clause(monkeypatch, capsys):
    mock_say = MagicMock()
    monkeypatch.setattr(play_lang_module, "say", mock_say)

    play_lang_module.play_ru(1)()

    mock_say.assert_called_once_with(lang="ru", text=PAIR.ru, voice=None)
    assert PAIR.ru in capsys.readouterr().out


def test_play_ru_speaks_only_the_given_clause(monkeypatch):
    mock_say = MagicMock()
    monkeypatch.setattr(play_lang_module, "say", mock_say)

    play_lang_module.play_ru(1, clause=1)()

    mock_say.assert_called_once_with(lang="ru", text=FIRST_CLAUSE_RU, voice=None)


def test_play_ru_passes_voice_through_to_say(monkeypatch):
    mock_say = MagicMock()
    monkeypatch.setattr(play_lang_module, "say", mock_say)

    play_lang_module.play_ru(1, clause=1, voice="irina")()

    mock_say.assert_called_once_with(lang="ru", text=FIRST_CLAUSE_RU, voice="irina")


# -- print_en / print_ru ------------------------------------------------------------


def test_print_en_fn_prints_without_speaking(monkeypatch, capsys):
    mock_say = MagicMock()
    monkeypatch.setattr(play_lang_module, "say", mock_say)

    play_lang_module.print_en(1, clause=1)()

    mock_say.assert_not_called()
    assert FIRST_CLAUSE_EN in capsys.readouterr().out


def test_print_ru_fn_prints_without_speaking(monkeypatch, capsys):
    mock_say = MagicMock()
    monkeypatch.setattr(play_lang_module, "say", mock_say)

    play_lang_module.print_ru(1, clause=1)()

    mock_say.assert_not_called()
    assert FIRST_CLAUSE_RU in capsys.readouterr().out


# -- render_en / render_ru -----------------------------------------------------------


def test_render_en_returns_lead_in_silence_plus_synthesized_clause(monkeypatch):
    monkeypatch.setattr(
        play_lang_module, "synthesize", lambda *, lang, text, voice: f"AUDIO[{lang}]:{text}".encode()
    )

    audio = play_lang_module.render_en(1, clause=1)

    expected_silence = play_lang_module.silence(play_lang_module.LEAD_IN_SECONDS)
    assert audio == expected_silence + f"AUDIO[en]:{FIRST_CLAUSE_EN}".encode()


def test_render_ru_returns_lead_in_silence_plus_synthesized_clause(monkeypatch):
    monkeypatch.setattr(
        play_lang_module, "synthesize", lambda *, lang, text, voice: f"AUDIO[{lang}]:{text}".encode()
    )

    audio = play_lang_module.render_ru(1, clause=1)

    expected_silence = play_lang_module.silence(play_lang_module.LEAD_IN_SECONDS)
    assert audio == expected_silence + f"AUDIO[ru]:{FIRST_CLAUSE_RU}".encode()


def test_render_ru_passes_voice_through_to_synthesize(monkeypatch):
    calls = []
    monkeypatch.setattr(
        play_lang_module,
        "synthesize",
        lambda *, lang, text, voice: calls.append((lang, text, voice)) or b"AUDIO",
    )

    play_lang_module.render_ru(1, clause=1, voice="irina")

    assert calls == [("ru", FIRST_CLAUSE_RU, "irina")]
