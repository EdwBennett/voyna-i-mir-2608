
from collections.abc import Callable
import time

def play_wait(seconds: int) -> Callable[[], None]:

    def en_fn():
        time.sleep(seconds)

    return en_fn
