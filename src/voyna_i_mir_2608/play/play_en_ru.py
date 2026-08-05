
import sys
from collections.abc import Callable

from voyna_i_mir_2608.play.play_call_response import play
from voyna_i_mir_2608.play.play_en import play_en
from voyna_i_mir_2608.play.play_ru import play_ru


def play_en_ru(id: int) -> None:
    fn_call: Callable[[], None] = play_en(id)
    fn_response: Callable[[], None] = play_ru(id)
    play(fn_call, fn_response)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: uv run play_en_ru.py <id>")
    play_en_ru(int(sys.argv[1]))
