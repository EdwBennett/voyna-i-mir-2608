from pathlib import Path

from voyna_i_mir_2608.db.sentence_pairs import SentencePairs, parse_page_list

JSON_PATH = Path(__file__).resolve().parent.parent / "src" / "voyna_i_mir_2608" / "db" / "50_russian_english_ipa.json"

if __name__ == "__main__":
    # Select sentences whose .id is 1, 3, 5, 6, 7, or 8
    SentencePairs(JSON_PATH) \
        .filter(parse_page_list("1,3,5-8")) \
        .execute(lambda s: print(f"{s.id}\n{s.en}\n{s.ru}"))
    print()

    # As a list
    subset = (
        SentencePairs(JSON_PATH)
        .filter(parse_page_list("1,3,5-8"))
        .to_list()
    )
