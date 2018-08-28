from acres.ngram import finder


def test__build_search_ngrams():
    context = "a b c d"

    expected = ("a", "a b", "a b c")
    actual = finder._build_search_ngrams(context)
    assert expected == actual

    expected = ("d", "c d", "b c d")
    actual = finder._build_search_ngrams(context, True)
    assert expected == actual


def test_find_embeddings(ngramstat, index):
    finder_constraints = finder.FinderConstraints(min_freq=1, max_count=100, min_num_tokens=1,
                                                  max_num_tokens=5)

    # Explicit context
    actual = finder.find_embeddings("<SEL>", "EKG", "¶", finder_constraints)
    expected = [(19, 'Physikalischer Status')]
    assert set(expected).issubset(actual)

    # Relax right context
    actual = finder.find_embeddings("<SEL>", "EKG", "<SEL>", finder_constraints)
    expected = [(19, 'Physikalischer Status')]
    assert set(expected).issubset(actual)

    # Relax left and right contexts
    actual = finder.find_embeddings("<SEL>", "EKG", "<SEL>", finder_constraints)
    expected = [(19, 'Physikalischer Status')]
    assert set(expected).issubset(actual)

    # Changing min_num_tokens should restrict results
    finder_constraints = finder.FinderConstraints(min_freq=1, max_count=100, min_num_tokens=28,
                                                  max_num_tokens=5)
    # "* EKG ¶", the only valid embedding, happens 27 times
    actual = finder.find_embeddings("<SEL>", "EKG", "<SEL>", finder_constraints)
    expected = [(19, 'Physikalischer Status')]
    assert not set(expected).issubset(actual)


def test_strip_frequencies():
    embeddings = [(42, "Abc Def, xyz"), (10, "aaaaaaa")]

    expected = ["Abc Def, xyz", "aaaaaaa"]
    actual = finder._strip_frequencies(embeddings)

    assert expected == actual