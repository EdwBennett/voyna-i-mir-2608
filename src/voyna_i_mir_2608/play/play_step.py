"""
from root/db/voyna_i_mir.sqlite for selected chapter_sequence
    write new-line to stdout
    write chapter_full_name to stdout
    write english_translation to stdout
    wait for space-bar press
    say.py --lang ru --text "<voyna_i_mir_russian>"
    write voyna_i_mir_russian to stdout
    write russian_transliteration to stdout
    wait for space-bar press
    repeat
"""

import sys
import termios
import tty
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlmodel import Session, create_engine, select
from db.models import Voyna_I_Mir
from core.say_sentence.say import say


def wait_for_space() -> bool:
    """Wait for space-bar. Returns False (instead of blocking forever) if the
    user asks to quit via 'q' or Ctrl-C, True on a normal space press."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while True:
            char = sys.stdin.read(1)
            if char == " ":
                return True
            if char in ("q", "\x03"):  # 'q' or Ctrl-C
                return False
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def play_step(chapter_sequence: int) -> None:
    db_path = PROJECT_ROOT / "db" / "voyna_i_mir.sqlite"
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        statement = (
            select(Voyna_I_Mir)
            .where(Voyna_I_Mir.chapter_sequence == chapter_sequence)
            .limit(1)
        )
        record = session.exec(statement).first()

    if record is None:
        print("No record found")
        return

    while True:
        print()
        print(record.chapter_full_name)
        print(record.english_translation)
        if not wait_for_space():
            print("Exiting.")
            return

        say(lang="ru", text=record.voyna_i_mir_russian)
        print(record.voyna_i_mir_russian)
        print(record.russian_transliteration)
        if not wait_for_space():
            print("Exiting.")
            return


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: uv run play_step.py <chapter_sequence>")
    play_step(int(sys.argv[1]))
