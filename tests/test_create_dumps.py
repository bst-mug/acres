from acres import create_dumps


def test_create_morpho_dump():
    actual = create_dumps.create_morpho_dump("tests/resources/lex.xml", "tests/resources/lex.xml")
    expected = {'gramm', 'nieren', 'herc', 'crancheit', 'cardio', 'arbeits', 'el', 'cammer', 'electro', 'coronar'}

    assert expected.issubset(actual)


def test_create_corpus_char_stat_dump():
    char_ngrams = create_dumps.create_corpus_char_stat_dump("tests/data")

    actual = len(char_ngrams)
    expected = 70980
    print(actual)
    assert expected == actual
