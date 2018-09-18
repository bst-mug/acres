from acres.evaluation import evaluation


def test_analyze_file(ngramstat):
    (precision, recall) = evaluation.analyze_file("tests/resources/workbench.tsv", evaluation.Strategy.WORD2VEC)
    assert 1.0 == precision
    assert 0.25 == recall
