"""Tests for scripts/make_ru_mp3.py.

Unit tests exercise make_ru_mp3() with render_ru()/ffmpeg mocked out, so no
audio is produced and no subprocess is spawned. A CLI-level test invokes the
script as a subprocess to check argparse wiring.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "make_ru_mp3.py"

_spec = importlib.util.spec_from_file_location("make_ru_mp3", SCRIPT_PATH)
make_ru_mp3_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_ru_mp3_module)


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        text=True,
        capture_output=True,
        check=False,
    )


# -- make_ru_mp3: argument validation -------------------------------------------------


def test_rejects_non_mp3_output():
    with pytest.raises(ValueError, match=r"must end with \.mp3"):
        make_ru_mp3_module.make_ru_mp3("1", "out.wav")


# -- make_ru_mp3: audio rendering ----------------------------------------------------


def test_builds_audio_and_invokes_ffmpeg(monkeypatch):
    monkeypatch.setattr(
        make_ru_mp3_module, "render_ru", lambda id_, voice=None: b"RU" + str(id_).encode()
    )
    mock_run = MagicMock()
    monkeypatch.setattr(make_ru_mp3_module.subprocess, "run", mock_run)

    make_ru_mp3_module.make_ru_mp3("1,3", "out.mp3")

    gap = make_ru_mp3_module.silence(make_ru_mp3_module.GAP_SECONDS)
    expected_audio = b"RU1" + gap + b"RU3" + gap
    assert mock_run.call_args.kwargs["input"] == expected_audio
    called_cmd = mock_run.call_args.args[0]
    assert called_cmd[0] == "ffmpeg"
    assert called_cmd[-1] == "out.mp3"
    assert mock_run.call_args.kwargs["check"] is True


def test_uses_denis_voice(monkeypatch):
    calls = []
    monkeypatch.setattr(
        make_ru_mp3_module,
        "render_ru",
        lambda id_, voice=None: calls.append(voice) or b"RU",
    )
    monkeypatch.setattr(make_ru_mp3_module.subprocess, "run", MagicMock())

    make_ru_mp3_module.make_ru_mp3("1", "out.mp3")

    assert calls == ["denis"]


def test_defaults_to_all_sentences_in_dataset(monkeypatch):
    seen_ids = []
    monkeypatch.setattr(
        make_ru_mp3_module,
        "render_ru",
        lambda id_, voice=None: seen_ids.append(id_) or b"RU",
    )
    monkeypatch.setattr(make_ru_mp3_module.subprocess, "run", MagicMock())

    make_ru_mp3_module.make_ru_mp3(None, "out.mp3")

    assert seen_ids == list(range(1, 51))


# -- CLI (argparse wiring) ------------------------------------------------------------


def test_cli_requires_output():
    result = run_cli(["1"])

    assert result.returncode == 2
    assert "required: -o/--output" in result.stderr


def test_cli_rejects_non_mp3_output():
    result = run_cli(["1", "-o", "out.wav"])

    assert result.returncode == 1
    assert "must end with .mp3" in result.stderr
