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
    expected = {1: '0002000\t¶', 2: '0000200\tder', 3: '0000100\tund'}

    assert expected == actual


def test_create_index():
    actual = create_dumps.create_index(resource_factory.get_ngramstat())
    expected = {'¶': {1}, 'der': {2}, 'und': {3}}

    assert expected == actual


def test_create_normalised_token_dump():
    actual = create_dumps.create_normalised_token_dump("tests/models/ngrams/ngramstat.txt")
    expected = {'', '100\tund', '200\tder\n', '2000\t¶\n'}

    assert expected == actual
