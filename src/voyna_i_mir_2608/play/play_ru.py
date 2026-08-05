
from typing import Callable, Optional

def play_ru(id: int) -> Callable[[], None]:

    def ru_fn():
        print (f"id = {id}")

    return ru_fn
