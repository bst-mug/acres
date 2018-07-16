from acres.nn import test


def test_nn():
    actual = test.find_candidates("WORD")
    expected = ["WabcOabcRabcDabc"]
    assert actual == expected
