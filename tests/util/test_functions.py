from itertools import islice

from acres.util import functions


def test_import_conf():
    corpus_path = functions.import_conf("CORPUS_PATH")
    assert isinstance(corpus_path, str)


def test_get_url():
    url = "https://github.com/bst-mug/acres"
    actual = functions.get_url(url)

    # 200 means OK
    assert 200 == actual.status_code
    assert "Acronym" in actual.text


def test_create_ngram_statistics():
    assert functions.create_ngram_statistics('a', 1, 1) == {'a': 1}
    assert functions.create_ngram_statistics('a b', 1, 1) == {'a': 1, 'b': 1}
    assert functions.create_ngram_statistics('a a', 1, 1) == {'a': 2}
    assert functions.create_ngram_statistics(
        'a b', 1, 2) == {'a': 1, 'b': 1, 'a b': 1}

    expected = {
        'a': 4,
        'ab': 1,
        'aa': 1,
        'ba': 1,
        'ddd': 1,
        'a ab': 1,
        'ab aa': 1,
        'aa a': 1,
        'a a': 2,
        'a ba': 1,
        'ba ddd': 1,
        'a ab aa': 1,
        'ab aa a': 1,
        'aa a a': 1,
        'a a a': 1,
        'a a ba': 1,
        'a ba ddd': 1,
        'a ab aa a': 1,
        'ab aa a a': 1,
        'aa a a a': 1,
        'a a a ba': 1,
        'a a ba ddd': 1}
    actual = functions.create_ngram_statistics('a ab aa a a a ba ddd', 1, 4)
    assert expected == actual


def test_random_sub_list():
    # We output the input list if the length requested is larger or equal to
    # the input length
    assert functions.random_sub_list(["a", "b"], 2) == ["a", "b"]
    assert functions.random_sub_list(["a", "b"], 3) == ["a", "b"]

    # TODO use Random.seed() so that the output is deterministic
    assert functions.random_sub_list(["a", "b"], 1) in [["a"], ["b"]]


def test_robust_text_import_from_dir():
    actual = functions.robust_text_import_from_dir("tests/data")
    print(str(len(actual)))
    assert len(actual) == 20


def test__partition():
    assert functions.partition('a', 5) == 1
    assert functions.partition('g', 5) == 1
    assert functions.partition('h', 5) == 2
    assert functions.partition('m', 5) == 2
    assert functions.partition('n', 5) == 3
    assert functions.partition('t', 5) == 3
    assert functions.partition('u', 5) == 4
    assert functions.partition('z', 5) == 4
    assert functions.partition('0', 5) == 0
    assert functions.partition('9', 5) == 0
    assert functions.partition('ö', 5) == 0

    assert functions.partition('a', 1) == 0
    assert functions.partition('z', 1) == 0
    assert functions.partition('9', 1) == 0


def test_sample():
    iterable = ['a', 'b', 'c']
    assert list(islice(functions.sample(iterable, 1.0), 100)) == iterable
    assert list(islice(functions.sample(iterable, 0.0), 100)) == []
