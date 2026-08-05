
from collections.abc import Callable
import time

def play_wait(seconds: int) -> Callable[[], None]:

    def en_fn():
        print()
        time.sleep(seconds)

    return en_fn
