"""Tests for say.py, the Piper TTS CLI wrapper.

Unit tests exercise the pure logic (voice lookup, path validation, and the
subprocess commands built for piper/aplay) with mocks, so they run without
piper or audio hardware installed. CLI-level tests invoke say.py as a
subprocess to check argument parsing and stdin handling, using only inputs
that don't reach piper/aplay (so no audio is produced). A skippable
integration test calls the real piper binary, if installed, to confirm
synthesis actually works end to end without playing the result.
"""

from __future__ import annotations

import os
import pty
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import voyna_i_mir_2608.say.say as say_module
from voyna_i_mir_2608.say.say import VoiceSpec

SAY_PY = Path(__file__).resolve().parent.parent / "src" / "voyna_i_mir_2608" / "say" / "say.py"

PIPER_AVAILABLE = say_module.PIPER_BIN.exists() and all(
    path.exists() for spec in say_module.LANGUAGES.values() for path in (spec.model, spec.model_config)
)


def run_cli(args: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SAY_PY), *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


# -- get_voice_spec ----------------------------------------------------------


@pytest.mark.parametrize("lang", ["en", "ru"])
def test_get_voice_spec_returns_known_language(lang):
    spec = say_module.get_voice_spec(lang)

    assert isinstance(spec, VoiceSpec)


def test_get_voice_spec_unsupported_language_raises():
    with pytest.raises(ValueError, match="Unsupported language: fr"):
        say_module.get_voice_spec("fr")


# -- validate_paths -----------------------------------------------------------


def test_validate_paths_success(monkeypatch, tmp_path):
    piper_bin = tmp_path / "piper"
    piper_bin.touch()
    model = tmp_path / "model.onnx"
    model.touch()
    model_config = tmp_path / "model.onnx.json"
    model_config.touch()

    monkeypatch.setattr(say_module, "PIPER_BIN", piper_bin)
    monkeypatch.setitem(say_module.LANGUAGES, "en", VoiceSpec(model=model, model_config=model_config))

    spec = say_module.validate_paths("en")

    assert spec.model == model
    assert spec.model_config == model_config


def test_validate_paths_missing_piper_binary_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(say_module, "PIPER_BIN", tmp_path / "nonexistent-piper")

    with pytest.raises(FileNotFoundError, match="Piper binary not found"):
        say_module.validate_paths("en")


def test_validate_paths_missing_model_raises(monkeypatch, tmp_path):
    piper_bin = tmp_path / "piper"
    piper_bin.touch()
    model_config = tmp_path / "model.onnx.json"
    model_config.touch()

    monkeypatch.setattr(say_module, "PIPER_BIN", piper_bin)
    monkeypatch.setitem(
        say_module.LANGUAGES,
        "en",
        VoiceSpec(model=tmp_path / "missing.onnx", model_config=model_config),
    )

    with pytest.raises(FileNotFoundError, match="Model not found"):
        say_module.validate_paths("en")


def test_validate_paths_missing_model_config_raises(monkeypatch, tmp_path):
    piper_bin = tmp_path / "piper"
    piper_bin.touch()
    model = tmp_path / "model.onnx"
    model.touch()

    monkeypatch.setattr(say_module, "PIPER_BIN", piper_bin)
    monkeypatch.setitem(
        say_module.LANGUAGES,
        "en",
        VoiceSpec(model=model, model_config=tmp_path / "missing.onnx.json"),
    )

    with pytest.raises(FileNotFoundError, match="Model config not found"):
        say_module.validate_paths("en")


# -- synthesize ----------------------------------------------------------------


def test_synthesize_invokes_piper_and_returns_stdout(monkeypatch):
    spec = VoiceSpec(model=Path("/fake/model.onnx"), model_config=Path("/fake/model.onnx.json"))
    monkeypatch.setattr(say_module, "validate_paths", lambda lang: spec)
    monkeypatch.setattr(say_module, "PIPER_BIN", Path("/fake/piper"))

    mock_run = MagicMock(return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=b"raw-audio-bytes"))
    monkeypatch.setattr(say_module.subprocess, "run", mock_run)

    result = say_module.synthesize(lang="en", text="hello world")

    assert result == b"raw-audio-bytes"
    (called_cmd,), called_kwargs = mock_run.call_args
    assert called_cmd == [
        "/fake/piper",
        "--model",
        str(spec.model),
        "--config",
        str(spec.model_config),
        "--output_raw",
    ]
    assert called_kwargs["input"] == b"hello world"
    assert called_kwargs["stdout"] == subprocess.PIPE
    assert called_kwargs["check"] is True


# -- say -------------------------------------------------------------------------


def test_say_plays_synthesized_audio(monkeypatch):
    monkeypatch.setattr(say_module, "synthesize", lambda *, lang, text: b"pcm-bytes")
    mock_run = MagicMock(return_value=subprocess.CompletedProcess(args=[], returncode=0))
    monkeypatch.setattr(say_module.subprocess, "run", mock_run)

    say_module.say(lang="en", text="hi")

    (called_cmd,), called_kwargs = mock_run.call_args
    assert called_cmd[0] == "aplay"
    assert str(say_module.SAMPLE_RATE) in called_cmd
    assert called_kwargs["input"] == b"pcm-bytes"
    assert called_kwargs["check"] is True


def test_say_reports_error_and_does_not_raise(monkeypatch, capsys):
    def boom(*, lang, text):
        raise RuntimeError("piper exploded")

    monkeypatch.setattr(say_module, "synthesize", boom)

    say_module.say(lang="en", text="hi")  # must not raise

    assert "Error during playback: piper exploded" in capsys.readouterr().err


# -- CLI (argparse / stdin handling) ---------------------------------------------


def test_cli_rejects_unsupported_language():
    result = run_cli(["-l", "fr", "bonjour"])

    assert result.returncode == 2
    assert "invalid choice: 'fr'" in result.stderr


def test_cli_warns_and_exits_zero_on_empty_stdin():
    result = run_cli(["-l", "en"], input_text="   \n")

    assert result.returncode == 0
    assert "Warning: Received empty text input" in result.stderr


def test_cli_warns_and_exits_zero_on_whitespace_only_arg():
    result = run_cli(["-l", "en", "   "])

    assert result.returncode == 0
    assert "Warning: Received empty text input" in result.stderr


def test_cli_errors_when_no_text_and_stdin_is_a_tty():
    master_fd, slave_fd = pty.openpty()
    try:
        result = subprocess.run(
            [sys.executable, str(SAY_PY)],
            stdin=slave_fd,
            text=True,
            capture_output=True,
            check=False,
        )
    finally:
        os.close(master_fd)
        os.close(slave_fd)

    assert result.returncode == 2
    assert "the following arguments are required: text" in result.stderr


# -- Integration (skipped unless piper + voice models are installed locally) ----


@pytest.mark.skipif(not PIPER_AVAILABLE, reason="piper binary or voice models not installed locally")
@pytest.mark.parametrize("lang, text", [("en", "Hello, this is a test."), ("ru", "Привет, это тест.")])
def test_synthesize_produces_audio_with_real_piper(lang, text):
    audio = say_module.synthesize(lang=lang, text=text)

    assert isinstance(audio, bytes)
    assert len(audio) > 0
