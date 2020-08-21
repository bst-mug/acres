from itertools import islice

from acres.word2vec import test


def test_nn(ngramstat):
    actual = test.find_candidates("WORD", min_distance=0)
    expected = "WabcOabcRabcDabc"
    assert expected in list(islice(actual, 10))
