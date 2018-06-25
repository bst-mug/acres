from acres import get_synonyms_from_ngrams


def test_find_embeddings():
    # Explicit context
    actual = get_synonyms_from_ngrams.find_embeddings("*", "EKG", "¶", 10, 1, 100, 1, 5)
    expected = ['0000019\tPhysikalischer Status']
    assert set(expected).issubset(actual)

    # Relax right context
    actual = get_synonyms_from_ngrams.find_embeddings("*", "EKG", "<SEL>", 10, 1, 100, 1, 5)
    expected = ['0000019\tPhysikalischer Status']
    assert set(expected).issubset(actual)

    # Relax left and right contexts
    actual = get_synonyms_from_ngrams.find_embeddings("<SEL>", "EKG", "<SEL>", 10, 1, 100, 1, 5)
    expected = ['0000019\tPhysikalischer Status']
    assert set(expected).issubset(actual)

    # Changing min_num_tokens should restrict results
    # "* EKG ¶", the only valid embedding, happens 27 times
    actual = get_synonyms_from_ngrams.find_embeddings("<SEL>", "EKG", "<SEL>", 10, 28, 100, 1, 5)
    expected = ['0000019\tPhysikalischer Status']
    assert not set(expected).issubset(actual)