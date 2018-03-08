from acres import get_synonyms_from_ngrams


def test_find_embeddings():
    actual = get_synonyms_from_ngrams.find_embeddings("re", "OL", "", 5, 1, 100, 6, 10)
    expected = []
    assert expected == actual

    actual = get_synonyms_from_ngrams.find_embeddings("*", "PDU", "*", 10, 3, 50, 1, 5)
    expected = []
    assert expected == actual
