from acres.evaluation import benchmark


def test_strip_frequencies():
    embeddings = ["0000042\tAbc Def, xyz", "0000010\taaaaaaa"]

    expected = ["Abc Def, xyz", "aaaaaaa"]
    actual = benchmark._strip_frequencies(embeddings)

    assert expected == actual
