from acres.preprocess import create_dumps, resource_factory


def test_create_morpho_dump():
    actual = create_dumps.create_morpho_dump("tests/resources/lex.xml")
    expected = {'gramm', 'nieren', 'herc', 'crancheit', 'cardio', 'arbeits', 'el', 'cammer', 'electro', 'coronar'}

    assert expected.issubset(actual)


def test_create_corpus_char_stat_dump():
    char_ngrams = create_dumps.create_corpus_char_stat_dump("tests/data")

    actual = len(char_ngrams)
    expected = 86187
    assert expected == actual


def test_create_corpus_ngramstat_dump():
    ngramstat = create_dumps.create_corpus_ngramstat_dump("tests/data", 2)

    # Check length
    actual = len(ngramstat)
    expected = 29597
    assert expected == actual

    # Baseline
    expected = {('¶', 2704), ('der', 450), ('EKG', 43)}
    assert set(expected).issubset(ngramstat.items())

    ngrams = ngramstat.keys()
    unique_ngrams = set(ngrams)

    # It should not have empty entries...
    assert "" not in unique_ngrams
    assert " " not in unique_ngrams

    # ...nor duplicate entries
    assert len(unique_ngrams) == len(ngrams)


def test_create_index(ngramstat):
    actual = create_dumps.create_index(ngramstat)
    expected = {'der': {1}, 'EKG': {2, 3}, 'Im': {3}}

    # Dictionary comparison
    for key, value in expected.items():
        assert value == actual[key]


def test_create_normalised_token_dump():
    actual = create_dumps.create_normalised_token_dump(
        "tests/models/ngrams/ngramstat.txt")
    expected = {'', 'EKG', '¶\n', '200\tder\n', '50\tEKG\n', 'status', '¶\n', '50\tekg\n', 'Status',
                '2000\t¶\n', '27\t*',
                'Physikalischer', 'physikalischer', 'physicalischer', '19\t*', 'Physicalischer', 'ekg'}

    assert set(expected).issubset(actual)


def test_create_acro_dumo():
    actual = create_dumps.create_acro_dump()
    expected = ['EKG']

    assert expected == actual


def test_create_new_acro_dumo():
    actual = create_dumps.create_new_acro_dump()
    expected = ['* EKG ¶']

    assert set(expected).issubset(actual)
