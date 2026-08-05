"""Text-to-speech helper using Piper for English and Russian.

Setup:
    uv tool install piper-tts     # installs `piper` to ~/.local/bin/piper
    Download the .onnx + .onnx.json pair for each language in LANGUAGES below
    from https://huggingface.co/rhasspy/piper-voices, mirroring its directory
    structure under ~/.local/share/piper-voices/ (e.g. en/en_US/amy/medium/...).

Test:
    uv run test_say.py
    uv run say.py -l ru "Война и миръ Графъ Л. Н. Толстой"
"""

from __future__ import annotations

import argparse
import dataclasses
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HOME = Path.home()
PIPER_BIN = HOME / ".local/bin/piper"
SAMPLE_RATE = 22050
LEAD_IN_SECONDS = 0.3
LANGUAGES: dict[str, VoiceSpec] = {}


@dataclass(frozen=True, slots=True)
class VoiceSpec:
    model: Path
    model_config: Path


LANGUAGES.update(
    {
        "en": VoiceSpec(
            model=HOME / ".local/share/piper-voices/en/en_US/amy/medium/en_US-amy-medium.onnx",
            model_config=HOME / ".local/share/piper-voices/en/en_US/amy/medium/en_US-amy-medium.onnx.json",
        ),
        "ru": VoiceSpec(
            model=HOME / ".local/share/piper-voices/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx",
            model_config=HOME / ".local/share/piper-voices/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx.json",
        ),
    }
)


def get_voice_spec(lang: str) -> VoiceSpec:
    try:
        return LANGUAGES[lang]
    except KeyError as exc:
        raise ValueError(f"Unsupported language: {lang}") from exc


def validate_paths(lang: str) -> VoiceSpec:
    spec = get_voice_spec(lang)
    
    if not PIPER_BIN.exists():
        raise FileNotFoundError(f"Piper binary not found at {PIPER_BIN}")
        
    for field_name, path in dataclasses.asdict(spec).items():
        if not path.exists():
            display_name = field_name.replace("_", " ").capitalize()
            raise FileNotFoundError(f"{display_name} not found at {path}")
            
    return spec


def synthesize(*, lang: str, text: str) -> bytes:
    """Render text to raw S16_LE mono PCM audio at SAMPLE_RATE, without playing it."""
    spec = validate_paths(lang)
    piper_cmd = [
        str(PIPER_BIN),
        "--model",
        str(spec.model),
        "--config",
        str(spec.model_config),
        "--output_raw",
    ]
    result = subprocess.run(
        piper_cmd,
        input=text.encode("utf-8"),
        stdout=subprocess.PIPE,
        check=True,
    )
    return result.stdout


def silence(duration_seconds: float) -> bytes:
    """Return zeroed S16_LE mono PCM audio of the requested duration at SAMPLE_RATE."""
    num_samples = int(SAMPLE_RATE * duration_seconds)
    return b"\x00" * (num_samples * 2)


def say(*, lang: str, text: str) -> None:
    play_cmd = [
        "aplay",
        "-c",
        "1",
        "-r",
        str(SAMPLE_RATE),
        "-f",
        "S16_LE",
        "-t",
        "raw",
    ]

    try:
        audio = synthesize(lang=lang, text=text)
        subprocess.run(play_cmd, input=silence(LEAD_IN_SECONDS) + audio, check=True)
    except Exception as exc:  # noqa: BLE001 - CLI safety net, always report and continue rather than crash
        print(f"Error during playback: {exc}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Piper TTS script.")
    parser.add_argument("-l", "--lang", default="en", choices=["en", "ru"], help="Language to use")
    # nargs="?" makes the argument optional; default=None lets us detect if it's missing
    parser.add_argument("text", nargs="?", default=None, help="Text to speak (reads from stdin if omitted)")
    args = parser.parse_args()

    # Determine text source
    if args.text is not None:
        text_to_speak = args.text.strip()
    elif not sys.stdin.isatty():
        # Read from pipe/redirected input and strip trailing whitespace/newlines
        text_to_speak = sys.stdin.read().strip()
    else:
        # User ran the script with no arguments and no pipe
        parser.error("the following arguments are required: text (or provide text via stdin)")

    if not text_to_speak:
        print("Warning: Received empty text input. Nothing to speak.", file=sys.stderr)
        sys.exit(0)

    try:
        say(lang=args.lang, text=text_to_speak)
    except Exception as error:  # noqa: BLE001 - CLI entry point, always exit cleanly rather than traceback
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
