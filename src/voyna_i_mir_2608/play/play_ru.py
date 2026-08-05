
from collections.abc import Callable


def play_ru(id: int) -> Callable[[], None]:

    def ru_fn():
        print (f"ru id = {id}")

    return ru_fn
