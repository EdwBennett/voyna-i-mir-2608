"""English and Russian playback for a sentence pair, keyed by id.

The two languages differ in what a "clause" is drawn from (English clauses
come from the `words` field, Russian clauses come from splitting `ru`
itself) and what gets printed alongside it (English shows the full sentence
plus either the word list or the clause; Russian shows the sentence or
clause plus its IPA transcription). Those differences are captured in
`_select_en_text`/`_select_ru_text` and `_print_en`/`_print_ru`; everything
else (loading, closures, mp3 rendering) is shared.
"""

from pathlib import Path
from typing import Literal, Optional
import re

from collections.abc import Callable
from voyna_i_mir_2608.db.sentence_pairs import SentencePair, SentencePairs
from voyna_i_mir_2608.say.say import LEAD_IN_SECONDS, say, silence, synthesize

JSON_PATH = Path(__file__).resolve().parent.parent / "db" / "50_russian_english_ipa_words.json"

Lang = Literal["en", "ru"]


def _load_pair(id_: int) -> SentencePair:
    """Look up the `SentencePair` with the given id in the bundled JSON dataset."""
    pairs = SentencePairs(JSON_PATH).filter([id_]).to_list()
    return pairs[0]


def _select_en_text(pair: SentencePair, clause: Optional[int]) -> str:
    """Return the full English sentence, or just one clause if `clause` is given."""
    if clause is None:
        return pair.en
    return re.split(r'[,.;-]+', pair.words)[clause - 1].strip()


def _select_ru_text(pair: SentencePair, clause: Optional[int]) -> str:
    """Return the full Russian sentence, or just one clause if `clause` is given."""
    if clause is None:
        return pair.ru
    return re.split(r'[,.;-]+', pair.ru)[clause - 1].strip()


def _print_en(pair: SentencePair, clause: Optional[int], en_say: str) -> None:
    """Print the English sentence (or `en_say`'s clause) for `pair` to stdout."""
    print(f"\n{pair.en}")
    if clause is None:
        print(f"{pair.words}")
    else:
        print(f"{en_say}")


def _print_ru(pair: SentencePair, clause: Optional[int], ru_say: str) -> None:
    """Print the Russian sentence (or `ru_say`'s clause) and its IPA transcription."""
    if clause is None:
        print(f"{pair.ru}")
    else:
        print(f"{ru_say}")
    print(f"{pair.ipa}\n")


_SELECT_TEXT: dict[Lang, Callable[[SentencePair, Optional[int]], str]] = {
    "en": _select_en_text,
    "ru": _select_ru_text,
}
_PRINT: dict[Lang, Callable[[SentencePair, Optional[int], str], None]] = {
    "en": _print_en,
    "ru": _print_ru,
}


def _play_fn(lang: Lang, id_: int, clause: Optional[int]) -> Callable[[], None]:
    """Return a function that prints and speaks the `lang` utterance for `id_`/`clause`."""

    def fn():
        pair = _load_pair(id_)
        text = _SELECT_TEXT[lang](pair, clause)
        _PRINT[lang](pair, clause, text)
        say(lang=lang, text=text)

    return fn


def _print_fn(lang: Lang, id_: int, clause: Optional[int]) -> Callable[[], None]:
    """Return a function that prints (without speaking) the `lang` utterance for `id_`/`clause`."""

    def fn():
        pair = _load_pair(id_)
        text = _SELECT_TEXT[lang](pair, clause)
        _PRINT[lang](pair, clause, text)

    return fn


def _render(lang: Lang, id_: int, clause: Optional[int]) -> bytes:
    """Synthesize the `lang` utterance for `id_`/`clause` without playing it."""
    pair = _load_pair(id_)
    text = _SELECT_TEXT[lang](pair, clause)
    return silence(LEAD_IN_SECONDS) + synthesize(lang=lang, text=text)


def play_en(id_: int, clause: Optional[int] = None) -> Callable[[], None]:
    """Return a function that prints and speaks the English utterance for `id_`/`clause`."""
    return _play_fn("en", id_, clause)


def play_ru(id_: int, clause: Optional[int] = None) -> Callable[[], None]:
    """Return a function that prints and speaks the Russian utterance for `id_`/`clause`."""
    return _play_fn("ru", id_, clause)


def print_en(id_: int, clause: Optional[int] = None) -> Callable[[], None]:
    """Print the English utterance for `id_`/`clause` without speaking it."""
    return _print_fn("en", id_, clause)


def print_ru(id_: int, clause: Optional[int] = None) -> Callable[[], None]:
    """Print the Russian utterance for `id_`/`clause` without speaking it."""
    return _print_fn("ru", id_, clause)


def render_en(id_: int, clause: Optional[int] = None) -> bytes:
    """Synthesize the English utterance for `id_`/`clause` without playing it."""
    return _render("en", id_, clause)


def render_ru(id_: int, clause: Optional[int] = None) -> bytes:
    """Synthesize the Russian utterance for `id_`/`clause` without playing it."""
    return _render("ru", id_, clause)
