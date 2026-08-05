
from collections.abc import Callable


def play_en(id: int) -> Callable[[], None]:

    def en_fn():
        print (f"en id = {id}")

    return en_fn
