from pathlib import Path

from collections.abc import Callable
from voyna_i_mir_2608.db.sentence_pairs import (
    SentencePair,
    SentencePairs,
    parse_id_list,
)

JSON_PATH = Path(__file__).resolve().parent.parent / "src" / "voyna_i_mir_2608" / "db" / "50_russian_english_ipa_words.json"

def play_en(id: int) -> Callable[[], None]:

    def en_fn():
        pairs = SentencePairs(JSON_PATH).filter([1]).to_list()
        pair = pairs[1]
        en_text: str = "english text" # pair.en
        words_text: str = "words text" # pair.words
        print (f"{pair.en} for id = {id}")
        print (f"{words_text} for id = {id}")

    return en_fn
