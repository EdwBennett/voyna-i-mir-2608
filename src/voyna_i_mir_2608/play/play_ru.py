
from collections.abc import Callable


def play_ru(id: int) -> Callable[[], None]:

    def ru_fn():
        ru_text: str = "russian text" # pair.ru
        ipa_text: str = "ipa text" # pair.ipa
        print (f"{ru_text} for id = {id}")
        print (f"{ipa_text} for id = {id}")


    return ru_fn
