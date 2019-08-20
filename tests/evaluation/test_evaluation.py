from acres.evaluation import evaluation
from acres.resolution import resolver


def test_analyze_file(ngramstat):
    (precision, recall) = evaluation.analyze_file("tests/resources/workbench.tsv",
                                                  resolver.Strategy.WORD2VEC, resolver.Level.TOKEN)
    assert 1.0 == precision
    assert 0.25 == recall


def test_do_analysis(ngramstat, capsys):
    evaluation.do_analysis("tests/resources/workbench.tsv", resolver.Strategy.WORD2VEC,
                           resolver.Level.TOKEN)
    captured = capsys.readouterr()

    expected = "F1:  0.4"
    actual = captured.out.split("\n")[-2]
    assert expected == actual
