"""Package entry point for `python -m voyna_i_mir_2608`.

Delegates directly to `voyna_i_mir_2608.play.play_en_ru.main` and exits
with its return code.

Usage:
    python -m voyna_i_mir_2608 <id> <delay> [clause] [--ru-voice {irina,denis}] [-o OUTPUT | -t | -i]

No external dependencies required.
"""

from voyna_i_mir_2608.play.play_en_ru import main

if __name__ == "__main__":
    raise SystemExit(main())
    