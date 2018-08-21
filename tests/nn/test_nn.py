from acres.nn import test


def test_nn(ngramstat):
    actual = test.find_candidates("WORD")
    expected = ["WabcOabcRabcDabc"]
    assert actual == expected
