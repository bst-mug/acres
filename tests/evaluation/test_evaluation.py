from acres.evaluation import evaluation


def test_analyze_file(ngramstat):
    (precision, recall) = evaluation.analyze_file("tests/resources/workbench.tsv", evaluation.Strategy.WORD2VEC)
    assert 1.0 == precision
    assert 0.25 == recall


def test_do_analysis(ngramstat, capsys):
    evaluation.do_analysis("tests/resources/workbench.tsv", evaluation.Strategy.WORD2VEC)
    captured = capsys.readouterr()

    expected = "F1:  0.4"
    actual = captured.out.split("\n")[-2]
    assert expected == actual
