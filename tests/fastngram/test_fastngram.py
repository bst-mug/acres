from itertools import islice

from acres.fastngram import fastngram
from acres.model.topic_list import Acronym


def test_expand(word_ngrams):
    expansions = list(islice(fastngram.expandn("EKG"), 100))
    assert len(expansions) == 9
    assert "Elektrokardiogramm" in expansions
    assert expansions[0] == "EKG"

    expansions = list(islice(fastngram.expandn("EKG", "performed", "yesterday"), 100))
    assert len(expansions) == 24
    assert "Elektro kardiogramm" in expansions
    assert expansions[0] == "EKG"


def test_baseline(word_ngrams):
    expansions = list(islice(fastngram.baseline("EKG"), 100))
    assert len(expansions) == 9


def test__generate_ngram_contexts():
    fastngram.MAX_DIFF = 1
    expected = [Acronym(left_context='', acronym='a', right_context='')]
    assert fastngram._generate_ngram_contexts("a") == expected

    expected = [Acronym(left_context='', acronym='a b', right_context=''),
                Acronym(left_context='', acronym='a', right_context='b'),
                Acronym(left_context='a', acronym='b', right_context='')]
    assert fastngram._generate_ngram_contexts("a b") == expected

    expected = [Acronym(left_context='', acronym='a b c', right_context=''),
                Acronym(left_context='', acronym='a b', right_context='c'),
                Acronym(left_context='a', acronym='b c', right_context=''),
                Acronym(left_context='a', acronym='b', right_context='c')]
    assert fastngram._generate_ngram_contexts("a b c") == expected

    expected = [Acronym(left_context='', acronym='a b c d', right_context=''),
                Acronym(left_context='', acronym='a b c', right_context='d'),
                Acronym(left_context='a', acronym='b c d', right_context=''),
                Acronym(left_context='a', acronym='b c', right_context='d'),
                Acronym(left_context='a', acronym='b', right_context='c d'),
                Acronym(left_context='a b', acronym='c', right_context='d')]
    assert fastngram._generate_ngram_contexts("a b c d") == expected

    expected = [Acronym(left_context='', acronym='a b c d e', right_context=''),
                Acronym(left_context='', acronym='a b c d', right_context='e'),
                Acronym(left_context='a', acronym='b c d e', right_context=''),
                Acronym(left_context='a', acronym='b c d', right_context='e'),
                Acronym(left_context='a', acronym='b c', right_context='d e'),
                Acronym(left_context='a b', acronym='c d', right_context='e'),
                Acronym(left_context='a b', acronym='c', right_context='d e')]
    assert fastngram._generate_ngram_contexts("a b c d e") == expected


def test__generate_acronym_contexts():
    fastngram.MAX_DIFF = 1

    # Baseline
    expected = [Acronym(left_context='a b c', acronym='d', right_context='e f g'),
                Acronym(left_context='b c', acronym='d', right_context='e f g'),
                Acronym(left_context='a b c', acronym='d', right_context='e f'),
                Acronym(left_context='b c', acronym='d', right_context='e f'),
                Acronym(left_context='c', acronym='d', right_context='e f'),
                Acronym(left_context='b c', acronym='d', right_context='e'),
                Acronym(left_context='c', acronym='d', right_context='e'),
                Acronym(left_context='', acronym='d', right_context='e'),
                Acronym(left_context='c', acronym='d', right_context=''),
                Acronym(left_context='', acronym='d', right_context='')]
    acronym = Acronym(left_context='a b c', acronym='d', right_context='e f g')
    assert fastngram._generate_acronym_contexts(acronym) == expected

    # Empty context
    expected = [Acronym(left_context='', acronym='a', right_context='')]
    acronym = Acronym(left_context='', acronym='a', right_context='')
    assert fastngram._generate_acronym_contexts(acronym) == expected

    # Longer left context
    expected = [Acronym(left_context='b c', acronym='d', right_context='e'),
                Acronym(left_context='c', acronym='d', right_context='e'),
                Acronym(left_context='', acronym='d', right_context='e'),
                Acronym(left_context='c', acronym='d', right_context=''),
                Acronym(left_context='', acronym='d', right_context='')]
    acronym = Acronym(left_context='a b c', acronym='d', right_context='e')
    assert fastngram._generate_acronym_contexts(acronym) == expected

    # Longer right context
    expected = [Acronym(left_context='a', acronym='b', right_context='c d'),
                Acronym(left_context='a', acronym='b', right_context='c'),
                Acronym(left_context='', acronym='b', right_context='c'),
                Acronym(left_context='a', acronym='b', right_context=''),
                Acronym(left_context='', acronym='b', right_context='')]
    acronym = Acronym(left_context='a', acronym='b', right_context='c d e')
    assert fastngram._generate_acronym_contexts(acronym) == expected
