from acres.fastngram.fastngram import expand


def test_expand(word_ngrams):
    expansions = expand("EKG")
    assert len(expansions) == 8
    assert "Elektrokardiogramm" in expansions
