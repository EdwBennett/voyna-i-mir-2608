from sentence_pairs import SentencePairs, parse_page_list

if __name__ == "__main__":
    # Select sentences whose .id is 1, 3, 5, 6, 7, or 8
    SentencePairs("50_russian_english_ipa.json") \
        .filter(parse_page_list("1,3,5-8")) \
        .execute(lambda s: print(s.id, s.en))

    # As a list
    subset = (
        SentencePairs("50_russian_english_ipa.json")
        .filter(parse_page_list("1,3,5-8"))
        .to_list()
    )
