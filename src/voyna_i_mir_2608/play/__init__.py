"""Orchestration of English/Russian sentence-pair playback and mp3 rendering.

See `voyna_i_mir_2608.play.play_en_ru` for the top-level entry point.
"""

from collections.abc import Callable


def play(fn_call: Callable[[], None] | None,
        fn_wait_before: Callable[[], None] | None,
        fn_response: Callable[[], None] | None,
        fn_wait_after: Callable[[], None] | None) -> None:
    """Executes a function call, a wait, the response, then another wait; any may be None."""
    if fn_call is not None:
        fn_call()
    if fn_wait_before is not None:
        fn_wait_before()
    if fn_response is not None:
        fn_response()
    if fn_wait_after is not None:
        fn_wait_after()
