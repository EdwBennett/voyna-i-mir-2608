"""Executes a call function followed by a response function."""

from collections.abc import Callable


def play(fn_call: Callable[[], None] | None, fn_response: Callable[[], None] | None) -> None:
    """Executes a function call followed by its response function, allowing either to be None."""
    if fn_call is not None:
        fn_call()
    if fn_response is not None:
        fn_response()
