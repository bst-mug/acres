from acres.fastngram import fastngram


def test_expand(word_ngrams):
    expansions = fastngram.expand("EKG")
    assert len(expansions) == 9
    assert "Elektrokardiogramm" in expansions
    assert expansions[0] == "EKG"

    expansions = fastngram.expand("EKG", "performed", "yesterday")
    assert len(expansions) == 12
    assert "Elektro kardiogramm" in expansions
    assert expansions[0] == "EKG"


def test_baseline(word_ngrams):
    expansions = fastngram.baseline("EKG")
    assert len(expansions) == 9
