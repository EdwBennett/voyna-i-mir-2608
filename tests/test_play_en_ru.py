"""Tests for play_en_ru.py, the top-level English/Russian playback driver.

Unit tests exercise play_en_ru()/_render_to_mp3() with say()/synthesize()/
ffmpeg mocked out, so no audio is produced and no subprocess is spawned.
A CLI-level test invokes the script as a subprocess to check the
mutually-exclusive -o/-t argparse wiring, without reaching real playback.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import voyna_i_mir_2608.play.play_en_ru as play_en_ru_module
import voyna_i_mir_2608.play.play_lang as play_lang_module
import voyna_i_mir_2608.play.play_wait as play_wait_module

PLAY_EN_RU_PY = Path(__file__).resolve().parent.parent / "src" / "voyna_i_mir_2608" / "play" / "play_en_ru.py"

PAIR = play_lang_module._load_pair(1)


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PLAY_EN_RU_PY), *args],
        text=True,
        capture_output=True,
        check=False,
    )


# -- play_en_ru: argument validation -----------------------------------------------


def test_play_en_ru_rejects_output_and_text_only_together():
    with pytest.raises(ValueError, match="mutually exclusive"):
        play_en_ru_module.play_en_ru("1", delay=1, output="out.mp3", text_only=True)


def test_play_en_ru_rejects_text_only_and_interactive_together():
    with pytest.raises(ValueError, match="mutually exclusive"):
        play_en_ru_module.play_en_ru("1", delay=1, text_only=True, interactive=True)


# -- play_en_ru: text_only mode -----------------------------------------------------


def test_play_en_ru_text_only_prints_without_speaking_or_waiting(monkeypatch, capsys):
    mock_say = MagicMock()
    mock_sleep = MagicMock()
    monkeypatch.setattr(play_lang_module, "say", mock_say)
    monkeypatch.setattr(play_wait_module.time, "sleep", mock_sleep)

    play_en_ru_module.play_en_ru("1", delay=5, text_only=True)

    mock_say.assert_not_called()
    mock_sleep.assert_not_called()
    out = capsys.readouterr().out
    assert PAIR.en in out
    assert PAIR.ru in out


# -- play_en_ru: live playback -------------------------------------------------------


def test_play_en_ru_speaks_english_then_waits_then_russian(monkeypatch):
    calls = []
    mock_say = MagicMock(side_effect=lambda *, lang, text: calls.append((lang, text)))
    mock_sleep = MagicMock(side_effect=lambda seconds: calls.append(("wait", seconds)))
    monkeypatch.setattr(play_lang_module, "say", mock_say)
    monkeypatch.setattr(play_wait_module.time, "sleep", mock_sleep)

    play_en_ru_module.play_en_ru("1", delay=3)

    # play() calls fn_wait both before and after the response.
    assert calls == [("en", PAIR.en), ("wait", 3), ("ru", PAIR.ru), ("wait", 3)]


def test_play_en_ru_interactive_waits_for_key_instead_of_sleeping(monkeypatch):
    calls = []
    mock_say = MagicMock(side_effect=lambda *, lang, text: calls.append((lang, text)))
    mock_sleep = MagicMock()
    mock_wait_key = MagicMock(return_value=lambda: calls.append(("key-wait",)))
    monkeypatch.setattr(play_lang_module, "say", mock_say)
    monkeypatch.setattr(play_wait_module.time, "sleep", mock_sleep)
    monkeypatch.setattr(play_en_ru_module, "play_wait_key", mock_wait_key)

    play_en_ru_module.play_en_ru("1", delay=3, interactive=True)

    mock_sleep.assert_not_called()
    # play() calls fn_wait both before and after the response.
    assert calls == [("en", PAIR.en), ("key-wait",), ("ru", PAIR.ru), ("key-wait",)]


def test_play_en_ru_processes_each_id_in_the_spec(monkeypatch):
    seen_ids = []
    monkeypatch.setattr(play_lang_module, "say", lambda *, lang, text: None)
    monkeypatch.setattr(play_wait_module.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(
        play_en_ru_module,
        "play_en",
        lambda id_, clause=None: (lambda: seen_ids.append(("en", id_))),
    )
    monkeypatch.setattr(
        play_en_ru_module,
        "play_ru",
        lambda id_, clause=None: (lambda: seen_ids.append(("ru", id_))),
    )

    play_en_ru_module.play_en_ru("1,3", delay=0)

    assert [id_ for _, id_ in seen_ids] == [1, 1, 3, 3]


# -- play_en_ru: mp3 rendering -------------------------------------------------------


def test_play_en_ru_renders_to_mp3_without_live_playback(monkeypatch, tmp_path):
    mock_say = MagicMock()
    monkeypatch.setattr(play_lang_module, "say", mock_say)
    monkeypatch.setattr(play_en_ru_module, "render_en", lambda id_, clause: b"EN")
    monkeypatch.setattr(play_en_ru_module, "render_ru", lambda id_, clause: b"RU")
    mock_run = MagicMock()
    monkeypatch.setattr(play_en_ru_module.subprocess, "run", mock_run)

    output = tmp_path / "out.mp3"
    play_en_ru_module.play_en_ru("1", delay=1, output=str(output))

    mock_say.assert_not_called()
    mock_run.assert_called_once()
    assert mock_run.call_args.args[0][-1] == str(output)


# -- _render_to_mp3 -------------------------------------------------------------------


def test_render_to_mp3_rejects_non_mp3_output():
    with pytest.raises(ValueError, match=r"must end with \.mp3"):
        play_en_ru_module._render_to_mp3([1], delay=1, clause=None, output="out.wav")


def test_render_to_mp3_builds_audio_and_invokes_ffmpeg(monkeypatch):
    monkeypatch.setattr(play_en_ru_module, "render_en", lambda id_, clause: b"EN" + str(id_).encode())
    monkeypatch.setattr(play_en_ru_module, "render_ru", lambda id_, clause: b"RU" + str(id_).encode())
    mock_run = MagicMock()
    monkeypatch.setattr(play_en_ru_module.subprocess, "run", mock_run)

    play_en_ru_module._render_to_mp3([1, 2], delay=1, clause=None, output="out.mp3")

    delay_silence = play_en_ru_module.silence(1)
    expected_audio = (
        b"EN1" + delay_silence + b"RU1" + delay_silence + b"EN2" + delay_silence + b"RU2" + delay_silence
    )
    assert mock_run.call_args.kwargs["input"] == expected_audio
    called_cmd = mock_run.call_args.args[0]
    assert called_cmd[0] == "ffmpeg"
    assert called_cmd[-1] == "out.mp3"
    assert mock_run.call_args.kwargs["check"] is True


# -- CLI (argparse wiring) ------------------------------------------------------------


def test_cli_rejects_output_and_text_only_together():
    result = run_cli(["1", "1", "-o", "out.mp3", "-t"])

    assert result.returncode == 2
    assert "not allowed with argument" in result.stderr


def test_cli_rejects_text_only_and_interactive_together():
    result = run_cli(["1", "1", "-t", "-i"])

    assert result.returncode == 2
    assert "not allowed with argument" in result.stderr


def test_cli_requires_id_and_delay():
    result = run_cli([])

    assert result.returncode == 2
    assert "required: id, delay" in result.stderr
