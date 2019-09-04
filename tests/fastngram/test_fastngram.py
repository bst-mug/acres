from itertools import islice

from acres.fastngram import fastngram


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
