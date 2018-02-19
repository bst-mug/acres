from .context import functions


def test_WordNgramStat():
    assert functions.create_ngram_statistics('a', 1, 1) == {'a': 1}
    assert functions.create_ngram_statistics('a b', 1, 1) == {'a': 1, 'b': 1}
    assert functions.create_ngram_statistics('a a', 1, 1) == {'a': 2}
    assert functions.create_ngram_statistics(
        'a b', 1, 2) == {'a': 1, 'b': 1, 'a b': 1}

    assert functions.create_ngram_statistics('a ab aa a a a ba ddd', 1, 4) == {'a': 4, 'ab': 1, 'aa': 1, 'ba': 1, 'ddd': 1, 'a ab': 1,
                                                                               'ab aa': 1, 'aa a': 1, 'a a': 2, 'a ba': 1, 'ba ddd': 1,
                                                                               'a ab aa': 1, 'ab aa a': 1, 'aa a a': 1, 'a a a': 1,
                                                                               'a a ba': 1, 'a ba ddd': 1, 'a ab aa a': 1,
                                                                               'ab aa a a': 1, 'aa a a a': 1, 'a a a ba': 1,
                                                                               'a a ba ddd': 1}
