from acres.preprocess import dumps


def test_create_corpus_ngramstat_dump():
    ngramstat = dumps.create_corpus_ngramstat_dump("tests/data", 100)
    actual = len(ngramstat)
    expected = 24
    assert expected == actual

    ngramstat = dumps.create_corpus_ngramstat_dump("tests/data", 2)

    # Check length
    actual = len(ngramstat)
    expected = 15860
    assert expected == actual

    # Baseline
    expected = {('der', 450), ('EKG', 66)}
    assert set(expected).issubset(ngramstat.items())

    ngrams = ngramstat.keys()
    unique_ngrams = set(ngrams)

    # It should not have empty entries...
    assert "" not in unique_ngrams
    assert " " not in unique_ngrams

    # ...nor duplicate entries
    assert len(unique_ngrams) == len(ngrams)
