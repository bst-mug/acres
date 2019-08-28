from acres.evaluation import evaluation
from acres.resolution import resolver


def test_do_analysis(ngramstat, capsys):
    evaluation.do_analysis("tests/resources/test_topics.tsv",
                           "tests/resources/test_detection.tsv",
                           "tests/resources/test_expansion.tsv",
                           resolver.Strategy.WORD2VEC, evaluation.Level.TOKEN, 10, True)
    captured = capsys.readouterr()

    expected = "F1:  0.4"
    actual = captured.out.split("\n")[-2]
    assert expected == actual
