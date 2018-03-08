from acres import create_dumps
from acres import resource_factory

def test_create_morpho_dump():
    actual = create_dumps.create_morpho_dump("tests/resources/lex.xml", "tests/resources/lex.xml")
    expected = {'gramm', 'nieren', 'herc', 'crancheit', 'cardio', 'arbeits', 'el', 'cammer', 'electro', 'coronar'}

    assert expected.issubset(actual)


def test_create_corpus_char_stat_dump():
    char_ngrams = create_dumps.create_corpus_char_stat_dump("tests/data")

    actual = len(char_ngrams)
    expected = 70980
    assert expected == actual


def test_create_ngramstat_dump():
    actual = create_dumps.create_ngramstat_dump("tests/models/ngrams/ngramstat.txt", 2)
    expected = {1: '0002000\t¶', 2: '0000200\tder', 3: '0000050\tEKG', 4: '0000020\tIm EKG'}

    assert expected == actual


def test_create_index():
    actual = create_dumps.create_index(resource_factory.get_ngramstat())
    expected = {'¶': {1}, 'der': {2}, 'EKG': {3, 4}, 'Im': {4}}

    assert expected == actual


def test_create_normalised_token_dump():
    actual = create_dumps.create_normalised_token_dump("tests/models/ngrams/ngramstat.txt")
    expected = {'', '50\tEKG\n', '20\tim', '2000\t¶\n', '50\tekg\n', '200\tder\n', 'EKG', 'ekg', '20\tIm'}

    print(actual)
    assert expected == actual


def test_create_acro_dumo():
    actual = create_dumps.create_acro_dump()
    expected = ['EKG']

    assert expected == actual


def test_create_new_acro_dumo():
    actual = create_dumps.create_new_acro_dump()
    expected = ['Im EKG']

    assert expected == actual
