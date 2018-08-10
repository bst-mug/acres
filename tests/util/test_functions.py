from acres.util import functions


def test_get_url():
    url = "https://github.com/bst-mug/acres"
    actual = functions.get_url(url)

    # 200 means OK
    assert 200 == actual.status_code
    assert "Acronym" in actual.text


def test_split_ngram():
    # pass
    assert functions.split_ngram("a b c") == []
    #
    assert functions.split_ngram("a AK b") == [('a', 'AK', 'b')]
    #
    assert functions.split_ngram("l ACR1 b ACR2 c") == [(
        'l', 'ACR1', 'b ACR2 c'), ('l ACR1 b', 'ACR2', 'c')]
    #
    assert functions.split_ngram("ACR") == [('', 'ACR', '')]


def test_fix_line_endings():
    expected = "This is a short text¶"
    actual = functions.fix_line_endings("This is a short text")
    assert expected == actual

    expected = "der Patientin¶"
    actual = functions.fix_line_endings("der\nPatientin")
    assert expected == actual

    expected = "DIAGNOSEN¶---------¶"
    actual = functions.fix_line_endings("DIAGNOSEN\n---------")
    assert expected == actual


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


def test_transliterate_to_seven_bit():
    assert "HAETTE" == functions.transliterate_to_seven_bit("hätte")
    assert "HATTE" == functions.transliterate_to_seven_bit("hätte", "en")

    assert "AANGSTROEM" == functions.transliterate_to_seven_bit("ångström")
    assert "ANGSTROM" == functions.transliterate_to_seven_bit("ångström", "en")


def test_substitute_k_and_f_by_context():
    assert "A" == functions.substitute_k_and_f_and_z_by_context("a")

    # Acronyms should not be substituted
    assert "aB" == functions.substitute_k_and_f_and_z_by_context("aB")
    assert "abCdef" == functions.substitute_k_and_f_and_z_by_context("abCdef")

    assert "PHARMACY" == functions.substitute_k_and_f_and_z_by_context("farmacy")

    assert "F" == functions.substitute_k_and_f_and_z_by_context("F")


def test_simplify_german_string():
    assert functions.simplify_german_string("LEBER") == "leber"

    assert functions.simplify_german_string("ekg") == "ecg"
    assert functions.simplify_german_string("heißen") == "heissen"
    assert functions.simplify_german_string(
        "Elektrokardiogramm") == "electrocardiogramm"

    # XXX Is it expected?
    assert functions.simplify_german_string("herz") == "herc"
    assert functions.simplify_german_string("café") == "cafe"


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
