from pathlib import Path
from typing import Optional
import re

from collections.abc import Callable
from voyna_i_mir_2608.db.sentence_pairs import (
    SentencePair,
    SentencePairs,
    parse_id_list,
)
from voyna_i_mir_2608.say.say import LEAD_IN_SECONDS, say, silence, synthesize

JSON_PATH = Path(__file__).resolve().parent.parent / "db" / "50_russian_english_ipa_words.json"


def _load_pair(id: int) -> SentencePair:
    pairs = SentencePairs(JSON_PATH).filter([id]).to_list()
    return pairs[0]


def _select_ru_text(pair: SentencePair, clause: Optional[int]) -> str:
    if clause is None:
        return pair.ru
    return re.split(r'[,.;-]+', pair.ru)[clause - 1].strip()


def _print_ru(pair: SentencePair, clause: Optional[int], ru_say: str) -> None:
    if clause is None:
        print (f"{pair.ru}")
    else:
        print (f"{ru_say}")
    print (f"{pair.ipa}\n")


def play_ru(id: int, clause: Optional[int] = None) -> Callable[[], None]:

    def ru_fn():
        pair = _load_pair(id)
        ru_say = _select_ru_text(pair, clause)
        _print_ru(pair, clause, ru_say)
        say(lang = "ru", text=ru_say)

    return ru_fn


def print_ru(id: int, clause: Optional[int] = None) -> Callable[[], None]:
    """Print the Russian utterance for `id`/`clause` without speaking it."""

    def fn():
        pair = _load_pair(id)
        ru_say = _select_ru_text(pair, clause)
        _print_ru(pair, clause, ru_say)

    return fn


def render_ru(id: int, clause: Optional[int] = None) -> bytes:
    """Synthesize the Russian utterance for `id`/`clause` without playing it."""
    pair = _load_pair(id)
    ru_say = _select_ru_text(pair, clause)
    return silence(LEAD_IN_SECONDS) + synthesize(lang="ru", text=ru_say)
