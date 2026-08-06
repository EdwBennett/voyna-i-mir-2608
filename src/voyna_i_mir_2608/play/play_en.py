"""English half of an English/Russian playback pair, keyed by sentence id."""

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
    """Look up the `SentencePair` with the given id in the bundled JSON dataset."""
    pairs = SentencePairs(JSON_PATH).filter([id]).to_list()
    return pairs[0]


def _select_en_text(pair: SentencePair, clause: Optional[int]) -> str:
    """Return the full English sentence, or just one clause if `clause` is given."""
    if clause is None:
        return pair.en
    return re.split(r'[,.;-]+', pair.words)[clause - 1].strip()


def _print_en(pair: SentencePair, clause: Optional[int], en_say: str) -> None:
    """Print the English sentence (or `en_say`'s clause) for `pair` to stdout."""
    print (f"\n{pair.en}")
    if clause is None:
        print (f"{pair.words}")
    else:
        print (f"{en_say}")


def play_en(id: int, clause: Optional[int] = None) -> Callable[[], None]:
    """Return a function that prints and speaks the English utterance for `id`/`clause`."""

    def en_fn():
        pair = _load_pair(id)
        en_say = _select_en_text(pair, clause)
        _print_en(pair, clause, en_say)
        say(lang = "en", text=en_say)

    return en_fn


def print_en(id: int, clause: Optional[int] = None) -> Callable[[], None]:
    """Print the English utterance for `id`/`clause` without speaking it."""

    def fn():
        pair = _load_pair(id)
        en_say = _select_en_text(pair, clause)
        _print_en(pair, clause, en_say)

    return fn


def render_en(id: int, clause: Optional[int] = None) -> bytes:
    """Synthesize the English utterance for `id`/`clause` without playing it."""
    pair = _load_pair(id)
    en_say = _select_en_text(pair, clause)
    return silence(LEAD_IN_SECONDS) + synthesize(lang="en", text=en_say)
