# sentence_pairs.py

import json
from dataclasses import dataclass
from typing import Callable, Any, List, Iterable, Dict

from py_range_parse import parse_range

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

        The numbers from parse_range(...) are treated as SentencePair.id values.
        Example:
          parse_range("1,3,5-8") → [1, 3, 5, 6, 7, 8]
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
        