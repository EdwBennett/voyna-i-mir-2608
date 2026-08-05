from pathlib import Path

from collections.abc import Callable
from voyna_i_mir_2608.db.sentence_pairs import (
    SentencePair,
    SentencePairs,
    parse_id_list,
)
from voyna_i_mir_2608.say.say import say

JSON_PATH = Path(__file__).resolve().parent.parent / "db" / "50_russian_english_ipa_words.json"

def play_ru(id: int) -> Callable[[], None]:

    def ru_fn():
        pairs = SentencePairs(JSON_PATH).filter([id]).to_list()
        pair = pairs[0]
        say(lang = "ru", text=pair.ru)
        print (f"{pair.ru}")
        print (f"{pair.ipa}")
        print (f"{pair.words}")


    return ru_fn
