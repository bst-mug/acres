from acres.preprocess import dumps, resource_factory


def test_create_morpho_dump():
    actual = dumps.create_morpho_dump("tests/resources/lex.xml")
    expected = {'gramm', 'nieren', 'herc', 'crancheit', 'cardio', 'arbeits', 'el', 'cammer', 'electro', 'coronar'}

    assert expected.issubset(actual)


def test_create_corpus_char_stat_dump():
    char_ngrams = dumps.create_corpus_char_stat_dump("tests/data")

    actual = len(char_ngrams)
    expected = 86187
    assert expected == actual


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


def test_create_index(ngramstat, index):
    actual = dumps.create_index(ngramstat)
    expected = index

    # Dictionary comparison
    for key, value in expected.items():
        assert value == actual[key]


def test_create_acro_dump(ngramstat):
    actual = dumps.create_acro_dump()
    expected = ['EKG']

    assert expected == actual


def test_create_new_acro_dump(ngramstat):
    actual = dumps.create_new_acro_dump()
    expected = ['Im EKG']

    assert set(expected).issubset(actual)
