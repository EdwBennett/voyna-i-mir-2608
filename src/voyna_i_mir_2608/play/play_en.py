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

def play_en(id: int, clause: Optional[int] = None) -> Callable[[], None]:

    def en_fn():
        pairs = SentencePairs(JSON_PATH).filter([id]).to_list()
        pair = pairs[0]
        print (f"\n{pair.en}")
        if clause is None:
            en_say: str = pair.en
            print (f"{pair.words}")
        else:
            en_say = re.split(r'[,.;-]+', pair.words)[clause-1].strip()
            print (f"{en_say}")
        say(lang = "en", text=en_say)

    return en_fn
