from itertools import islice

from acres.fastngram import fastngram
from acres.model.topic_list import Acronym


def test_expand(word_ngrams):
    expansions = list(islice(fastngram.expandn("EKG"), 100))
    assert len(expansions) == 9
    assert "Elektrokardiogramm" in expansions
    assert expansions[0] == "EKG"

    expansions = list(islice(fastngram.expandn("EKG", "performed", "yesterday"), 100))
    assert len(expansions) == 12
    assert "Elektro kardiogramm" in expansions
    assert expansions[0] == "EKG"


def test_baseline(word_ngrams):
    expansions = list(islice(fastngram.baseline("EKG"), 100))
    assert len(expansions) == 9


def test__generate_ngram_contexts():
    expected = [Acronym(left_context='', acronym='a', right_context='')]
    assert fastngram._generate_ngram_contexts("a") == expected

    expected = [Acronym(left_context='', acronym='a b', right_context='')]
    assert fastngram._generate_ngram_contexts("a b") == expected

    expected = [Acronym(left_context='', acronym='a b c', right_context=''),
                Acronym(left_context='a', acronym='b', right_context='c')]
    assert fastngram._generate_ngram_contexts("a b c") == expected

    expected = [Acronym(left_context='', acronym='a b c d', right_context=''),
                Acronym(left_context='a', acronym='b c', right_context='d')]
    assert fastngram._generate_ngram_contexts("a b c d") == expected

    expected = [Acronym(left_context='', acronym='a b c d e', right_context=''),
                Acronym(left_context='a', acronym='b c d', right_context='e'),
                Acronym(left_context='a b', acronym='c', right_context='d e')]
    assert fastngram._generate_ngram_contexts("a b c d e") == expected
