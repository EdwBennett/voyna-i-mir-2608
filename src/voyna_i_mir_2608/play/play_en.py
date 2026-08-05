from pathlib import Path

from collections.abc import Callable
from voyna_i_mir_2608.db.sentence_pairs import (
    SentencePair,
    SentencePairs,
    parse_id_list,
)
from voyna_i_mir_2608.say.say import say

JSON_PATH = Path(__file__).resolve().parent.parent / "db" / "50_russian_english_ipa_words.json"

def play_en(id: int) -> Callable[[], None]:

    def en_fn():
        pairs = SentencePairs(JSON_PATH).filter([id]).to_list()
        pair = pairs[0]
        print (f"\n{pair.en}")
        say(lang = "en", text=pair.en)

    return en_fn
