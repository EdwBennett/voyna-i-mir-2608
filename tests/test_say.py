"""Manual smoke test for say.py. Don't run with: uv run test_say.py"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HOME = Path.home()
SAY_PY = Path(__file__).parent / "say.py"

VOICE_FILES = [
    HOME / ".local/share/piper-voices/en/en_US/amy/medium/en_US-amy-medium.onnx",
    HOME / ".local/share/piper-voices/en/en_US/amy/medium/en_US-amy-medium.onnx.json",
    HOME / ".local/share/piper-voices/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx",
    HOME / ".local/share/piper-voices/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx.json",
]


def check_preconditions() -> None:
    print("== preconditions ==")
    piper_bin = HOME / ".local/bin/piper"
    print(f"{'OK' if piper_bin.exists() else 'FAIL'}: {piper_bin}")
    for f in VOICE_FILES:
        print(f"{'OK' if f.exists() else 'FAIL'}: {f}")


def run(label: str, args: list[str], *, input_text: str | None = None) -> None:
    print(f"== {label} ==")
    result = subprocess.run(
        [sys.executable, str(SAY_PY), *args],
        input=input_text,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")
    print(f"exit code: {result.returncode}")


if __name__ == "__main__":
    check_preconditions()
    run("English, arg form", ["-l", "en", "Hello, this is a test."])
    run("Russian, arg form", ["-l", "ru", "Привет, это тест."])
    run("default language (en)", ["Default language check."])
    run("stdin form", ["-l", "en"], input_text="Reading this from standard input.\n")
    run("empty stdin (should warn, exit 0)", ["-l", "en"], input_text="")
    run("unsupported language (argparse rejects it, exit 2)", ["-l", "fr", "bonjour"])
