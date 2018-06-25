from acres.evaluation import benchmark


def test_strip_frequencies():
    embeddings = [(42, "Abc Def, xyz"), (10, "aaaaaaa")]

    expected = ["Abc Def, xyz", "aaaaaaa"]
    actual = benchmark._strip_frequencies(embeddings)

    assert expected == actual
