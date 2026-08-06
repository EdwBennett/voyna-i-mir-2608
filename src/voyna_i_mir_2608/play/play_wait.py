"""A pause step between English and Russian playback in a `play()` sequence."""

from collections.abc import Callable
import sys
import termios
import time
import tty

def play_wait(seconds: int) -> Callable[[], None]:
    """Return a function that prints a blank line then sleeps for `seconds`."""

    def fn():
        print()
        time.sleep(seconds)

    return fn

def play_wait_key() -> Callable[[], None]:
    """Return a function that prints a blank line then blocks until the space bar is pressed."""

    def fn():
        print()
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while sys.stdin.read(1) != " ":
                pass
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return fn
