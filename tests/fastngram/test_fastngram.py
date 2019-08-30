from acres.fastngram.fastngram import expand


def test_expand(word_ngrams):
    expansions = expand("EKG")
    assert "Elektrokardiogramm" in expansions
