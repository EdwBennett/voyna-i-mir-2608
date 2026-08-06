"""Tests for say.py, the Piper TTS CLI wrapper.

Unit tests exercise the pure logic (voice lookup, path validation, and the
subprocess commands built for piper/aplay) with mocks, so they run without
piper or audio hardware installed. CLI-level tests invoke say.py as a
subprocess to check argument parsing and stdin handling, using only inputs
that don't reach piper/aplay (so no audio is produced). A skippable
integration test calls the real piper binary, if installed, to confirm
synthesis actually works end to end without playing the result.
"""

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

_ALL_SPECS = list(say_module.LANGUAGES.values()) + [
    spec for voices in say_module.VOICES.values() for spec in voices.values()
]
PIPER_AVAILABLE = say_module.PIPER_BIN.exists() and all(
    path.exists() for spec in _ALL_SPECS for path in (spec.model, spec.model_config)
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


@pytest.mark.parametrize("voice", ["irina", "denis"])
def test_get_voice_spec_returns_named_ru_voice(voice):
    spec = say_module.get_voice_spec("ru", voice)

    assert spec == say_module.VOICES["ru"][voice]


def test_get_voice_spec_defaults_to_denis_when_voice_omitted():
    assert say_module.get_voice_spec("ru") == say_module.VOICES["ru"]["denis"]


def test_get_voice_spec_unsupported_voice_raises():
    with pytest.raises(ValueError, match="Unsupported voice for ru: bogus"):
        say_module.get_voice_spec("ru", "bogus")


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
    monkeypatch.setattr(say_module, "validate_paths", lambda lang, voice: spec)
    monkeypatch.setattr(say_module, "PIPER_BIN", Path("/fake/piper"))

    mock_run = MagicMock(return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=b"raw-audio-bytes"))
    monkeypatch.setattr(say_module.subprocess, "run", mock_run)

    result = say_module.synthesize(lang="en", text="hello world")

    assert result == b"raw-audio-bytes"
    called_cmd = mock_run.call_args.args[0]
    called_kwargs = mock_run.call_args.kwargs
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


def test_synthesize_passes_voice_through_to_validate_paths(monkeypatch):
    spec = VoiceSpec(model=Path("/fake/model.onnx"), model_config=Path("/fake/model.onnx.json"))
    calls = []
    monkeypatch.setattr(say_module, "validate_paths", lambda lang, voice: calls.append((lang, voice)) or spec)
    monkeypatch.setattr(say_module, "PIPER_BIN", Path("/fake/piper"))
    monkeypatch.setattr(
        say_module.subprocess,
        "run",
        MagicMock(return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=b"")),
    )

    say_module.synthesize(lang="ru", text="hi", voice="irina")

    assert calls == [("ru", "irina")]


# -- silence -------------------------------------------------------------------


def test_silence_is_zeroed_s16le_mono_of_requested_duration():
    audio = say_module.silence(0.25)

    # 0.25s at 22050 Hz, 16-bit mono: 5512 samples (truncated) * 2 bytes/sample.
    assert audio == b"\x00" * 11024


# -- say -------------------------------------------------------------------------


def test_say_plays_synthesized_audio(monkeypatch):
    monkeypatch.setattr(say_module, "synthesize", lambda *, lang, text, voice: b"pcm-bytes")
    mock_run = MagicMock(return_value=subprocess.CompletedProcess(args=[], returncode=0))
    monkeypatch.setattr(say_module.subprocess, "run", mock_run)

    say_module.say(lang="en", text="hi")

    called_cmd = mock_run.call_args.args[0]
    called_kwargs = mock_run.call_args.kwargs
    assert called_cmd[0] == "aplay"
    assert str(say_module.SAMPLE_RATE) in called_cmd
    assert called_kwargs["input"] == say_module.silence(say_module.LEAD_IN_SECONDS) + b"pcm-bytes"
    assert called_kwargs["check"] is True


def test_say_passes_voice_through_to_synthesize(monkeypatch):
    calls = []
    monkeypatch.setattr(
        say_module, "synthesize", lambda *, lang, text, voice: calls.append((lang, text, voice)) or b"pcm"
    )
    monkeypatch.setattr(say_module.subprocess, "run", MagicMock())

    say_module.say(lang="ru", text="привет", voice="irina")

    assert calls == [("ru", "привет", "irina")]


def test_say_reports_error_and_does_not_raise(monkeypatch, capsys):
    def boom(*, lang, text, voice):
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
@pytest.mark.parametrize(
    "lang, text, voice",
    [
        ("en", "Hello, this is a test.", None),
        ("ru", "Привет, это тест.", None),
        ("ru", "Привет, это тест.", "irina"),
        ("ru", "Привет, это тест.", "denis"),
    ],
)
def test_synthesize_produces_audio_with_real_piper(lang, text, voice):
    audio = say_module.synthesize(lang=lang, text=text, voice=voice)

    assert isinstance(audio, bytes)
    assert len(audio) > 0
