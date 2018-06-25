from acres import get_synonyms_from_ngrams


def test_find_embeddings():
    actual = get_synonyms_from_ngrams.find_embeddings("re", "OL", "<VOID>", 5, 1, 100, 6, 10)
    expected = []
    assert expected == actual

    actual = get_synonyms_from_ngrams.find_embeddings("<SEL>", "PDU", "<SEL>", 10, 3, 50, 1, 5)
    expected = []
    assert expected == actual

    actual = get_synonyms_from_ngrams.find_embeddings("<SEL>", "EKG", "<SEL>", 10, 3, 50, 1, 5)
    expected = ['0000019\tPhysikalischer Status']
    assert set(expected).issubset(actual)