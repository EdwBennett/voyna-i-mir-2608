from pathlib import Path
from typing import Optional
import re

from collections.abc import Callable
from voyna_i_mir_2608.db.sentence_pairs import (
    SentencePair,
    SentencePairs,
    parse_id_list,
)
from voyna_i_mir_2608.say.say import say

JSON_PATH = Path(__file__).resolve().parent.parent / "db" / "50_russian_english_ipa_words.json"

def play_ru(id: int, clause: Optional[int] = None) -> Callable[[], None]:

    def ru_fn():
        pairs = SentencePairs(JSON_PATH).filter([id]).to_list()
        pair = pairs[0]
        if clause is None:
            ru_say: str = pair.ru
            print (f"{pair.ru}")
        else:
            ru_say = re.split(r'[,.;-]+', pair.ru)[clause-1].strip()
            print (f"{ru_say}")
        print (f"{pair.ipa}\n")
        say(lang = "ru", text=ru_say)

    return ru_fn
