from acres.util import functions


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
