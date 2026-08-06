
import sys
from collections.abc import Callable
from typing import Optional

from voyna_i_mir_2608.play.play import play
from voyna_i_mir_2608.play.play_en import play_en
from voyna_i_mir_2608.play.play_wait import play_wait
from voyna_i_mir_2608.play.play_ru import play_ru


def play_en_ru(id: int, delay: int, clause: Optional[int] = None) -> None:
    fn_call: Callable[[], None] = play_en(id, clause)
    fn_wait: Callable[[], None] = play_wait(delay)
    fn_response: Callable[[], None] = play_ru(id, clause)
    play(fn_call, fn_wait, fn_response)


if __name__ == "__main__":
    # Require at least id and delay
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        raise SystemExit("Usage: uv run play_en_ru.py <id> <delay> [<clause>]")

    id_ = int(sys.argv[1])
    delay = int(sys.argv[2])

    # Optional clause: use a default if not provided
    clause = int(sys.argv[3]) if len(sys.argv) == 4 else None

    play_en_ru(id_, delay=delay, clause=clause)
