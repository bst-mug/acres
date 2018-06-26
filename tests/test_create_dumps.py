from acres.preprocess import create_dumps, resource_factory


def test_create_morpho_dump():
    actual = create_dumps.create_morpho_dump("tests/resources/lex.xml")
    expected = {'gramm', 'nieren', 'herc', 'crancheit', 'cardio', 'arbeits', 'el', 'cammer', 'electro', 'coronar'}

    assert expected.issubset(actual)


def test_create_corpus_char_stat_dump():
    char_ngrams = create_dumps.create_corpus_char_stat_dump("tests/data")

    actual = len(char_ngrams)
    expected = 70980
    assert expected == actual


def test_create_corpus_ngramstat_dump():
    ngramstat = create_dumps.create_corpus_ngramstat_dump("tests/data")

    actual = len(ngramstat)
    expected = 69569
    assert expected == actual


def test_create_ngramstat_dump():
    actual = create_dumps.create_ngramstat_dump("tests/models/ngrams/ngramstat.txt", 2)
    expected = {1: '0002000\t¶', 2: '0000200\tder', 3: '0000050\tEKG'}

    assert set(expected.values()).issubset(actual.values())


def test_create_index():
    actual = create_dumps.create_index(resource_factory.get_ngramstat())
    expected = {'¶': {1, 4, 6}, 'der': {2}, 'EKG': {3, 4, 5}, '*': {4, 6}, 'Im': {5}, 'Physikalischer': {6},
                'Status': {6}}

    assert expected == actual


def test_create_normalised_token_dump():
    actual = create_dumps.create_normalised_token_dump("tests/models/ngrams/ngramstat.txt")
    expected = {'', 'EKG', '¶\n', '200\tder\n', '50\tEKG\n', 'status', '¶', '50\tekg\n', 'Status', '2000\t¶\n', '27\t*',
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
