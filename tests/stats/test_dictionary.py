from acres.stats import dictionary


def test_dump_sample():
    expected = ['AA\tAlopecia areata', 'γ-GT\tγ-Glutamyltransferase']
    actual = dictionary.dump_sample()
    assert set(expected).issubset(actual)


def test_show_extremes(capsys):
    dictionary.show_extremes("", [], 1, 1)
    expected = "List too small"
    captured = capsys.readouterr()
    actual = captured.out.split("\n")[-2]
    assert expected == actual

    dictionary.show_extremes("", ["a", "b", "c"], 1, 1)
    expected = ["a", "(...)", "c"]
    captured = capsys.readouterr()
    actual = captured.out.split("\n")[-4:-1]
    assert expected == actual


def test_ratio_acro_words():
    expected = (0.43, 'DSM', 'Diagnostic and Statistical Manual of Mental Disorders')
    actual = dictionary.ratio_acro_words("DSM\tDiagnostic and Statistical Manual of Mental Disorders")
    assert expected == actual
