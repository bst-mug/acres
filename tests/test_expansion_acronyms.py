from acres import expansion_acronyms


def test_find_acronym_expansion():
    ngrams = []
    actual = expansion_acronyms.find_acronym_expansion(ngrams)
    expected = None

    assert expected == actual