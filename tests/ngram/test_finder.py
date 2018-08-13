from acres.ngram import finder


def test_find_embeddings():
    # Explicit context
    actual = finder.find_embeddings("*", "EKG", "¶", 10, 1, 100, 1, 5)
    expected = [(19, 'Physikalischer Status')]
    assert set(expected).issubset(actual)

    # Relax right context
    actual = finder.find_embeddings("*", "EKG", "<SEL>", 10, 1, 100, 1, 5)
    expected = [(19, 'Physikalischer Status')]
    assert set(expected).issubset(actual)

    # Relax left and right contexts
    actual = finder.find_embeddings("<SEL>", "EKG", "<SEL>", 10, 1, 100, 1, 5)
    expected = [(19, 'Physikalischer Status')]
    assert set(expected).issubset(actual)

    # Changing min_num_tokens should restrict results
    # "* EKG ¶", the only valid embedding, happens 27 times
    actual = finder.find_embeddings("<SEL>", "EKG", "<SEL>", 10, 28, 100, 1, 5)
    expected = [(19, 'Physikalischer Status')]
    assert not set(expected).issubset(actual)


def test_strip_frequencies():
    embeddings = [(42, "Abc Def, xyz"), (10, "aaaaaaa")]

    expected = ["Abc Def, xyz", "aaaaaaa"]
    actual = finder._strip_frequencies(embeddings)

    assert expected == actual