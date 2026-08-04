from pathlib import Path

import pytest

from voyna_i_mir_2608.db.sentence_pairs import SentencePair, SentencePairs, parse_page_list

JSON_PATH = Path(__file__).resolve().parent.parent / "src" / "voyna_i_mir_2608" / "db" / "50_russian_english_ipa.json"


@pytest.mark.parametrize(
    "spec, expected",
    [
        ("1", [1]),
        ("1,3", [1, 3]),
        ("5-8", [5, 6, 7, 8]),
        ("1,3,5-8", [1, 3, 5, 6, 7, 8]),
    ],
)
def test_parse_page_list(spec, expected):
    assert parse_page_list(spec) == expected


def test_filter_selects_matching_ids():
    subset = SentencePairs(JSON_PATH).filter(parse_page_list("1,3,5-8")).to_list()

    assert [s.id for s in subset] == [1, 3, 5, 6, 7, 8]
    assert all(isinstance(s, SentencePair) for s in subset)


def test_filter_excludes_non_matching_ids():
    subset = SentencePairs(JSON_PATH).filter([1]).to_list()

    assert len(subset) == 1
    assert subset[0].id == 1


def test_execute_calls_fn_for_each_filtered_item():
    seen = []

    SentencePairs(JSON_PATH).filter(parse_page_list("1,3,5-8")).execute(lambda s: seen.append(s.id))

    assert seen == [1, 3, 5, 6, 7, 8]


def test_to_list_without_filter_returns_all_items():
    subset = SentencePairs(JSON_PATH).to_list()

    assert len(subset) == 50
    assert subset[0].id == 1
