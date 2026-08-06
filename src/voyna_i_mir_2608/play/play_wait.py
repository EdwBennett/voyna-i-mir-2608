"""A pause step between English and Russian playback in a `play()` sequence."""

from collections.abc import Callable
from typing import Optional
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

def play_wait_key(
    repeat_key: Optional[str] = None,
    repeat_fn: Optional[Callable[[], None]] = None,
) -> Callable[[], None]:
    """Return a function that prints which keys are waited on, then blocks until the space bar is pressed.

    If `repeat_key` is given, pressing it calls `repeat_fn` and resumes
    waiting instead of returning; any other key is ignored. Terminal mode is
    restored around the `repeat_fn` call so its output isn't staircased by
    raw mode's disabled CR-on-LF.
    """

    def fn():
        if repeat_key is not None:
            print(f"[space] continue, [{repeat_key}] replay")
        else:
            print("[space] continue")
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch == " ":
                    return
                if repeat_key is not None and ch == repeat_key:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    repeat_fn()
                    tty.setraw(fd)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return fn
