"""Load and filter Russian/English sentence pairs with IPA transcriptions.

Provides `SentencePairs`, a small chainable loader over a JSON file of
records shaped like:

    {"id": 1, "ru": "...", "ipa": "[...]", "en": "..."}

and `parse_page_list`, which parses printer-style page/id specs like
"1,3,5-8" into an explicit list of integers for use with `.filter()`.

Typical usage (as a library, no CLI):

    from voyna_i_mir_2608.db.sentence_pairs import SentencePairs, parse_page_list

    pairs = SentencePairs("50_russian_english_ipa.json")
    ids = parse_page_list("1,3,5-8")
    for pair in pairs.filter(ids).to_list():
        print(pair.ru, pair.en)
        
    SentencePairs(JSON_PATH).filter(parse_page_list("1,3,5-8")).execute(
        lambda pair: print(pair.ru, pair.ipa, pair.en)
    )


No external dependencies beyond the standard library.
"""

import json
from dataclasses import dataclass
from typing import Callable, Any, List, Iterable, Dict


def parse_page_list(spec: str) -> List[int]:
    """
    Parse a printer-style page list, e.g. "1,3,5-8" -> [1, 3, 5, 6, 7, 8].
    """
    result: List[int] = []
    for part in spec.split(","):
        if "-" in part:
            start, end = part.split("-")
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(part))
    return result


@dataclass
class SentencePair:
    id: int
    ru: str
    ipa: str
    en: str

class SentencePairs:
    def __init__(self, path: str):
        self.path = path
        self._filters: List[Callable[[List[SentencePair]], List[SentencePair]]] = []

    def _load_all(self) -> List[SentencePair]:
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [SentencePair(**item) for item in data]

    def filter(self, pages: Iterable[int]) -> "SentencePairs":
        """
        Filter by ID values (not positions).

        The numbers from parse_page_list(...) are treated as SentencePair.id values.
        Example:
          parse_page_list("1,3,5-8") → [1, 3, 5, 6, 7, 8]
          This will select all SentencePair objects whose .id is in {1,3,5,6,7,8}.
        """
        wanted_ids = set(pages)

        def _filter(items: List[SentencePair]) -> List[SentencePair]:
            return [item for item in items if item.id in wanted_ids]

        self._filters.append(_filter)
        return self

    def _filtered_items(self) -> List[SentencePair]:
        items = self._load_all()
        for f in self._filters:
            items = f(items)
        return items

    def execute(self, fn: Callable[[SentencePair], Any]) -> None:
        """Run `fn` on each filtered SentencePair."""
        for obj in self._filtered_items():
            fn(obj)

    def to_list(self) -> List[SentencePair]:
        """Return filtered items as a list."""
        return self._filtered_items()
        