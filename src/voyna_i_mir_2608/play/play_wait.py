"""A pause step between English and Russian playback in a `play()` sequence."""

from collections.abc import Callable
import time

def play_wait(seconds: int) -> Callable[[], None]:
    """Return a function that prints a blank line then sleeps for `seconds`."""

    def en_fn():
        print()
        time.sleep(seconds)

    return en_fn
