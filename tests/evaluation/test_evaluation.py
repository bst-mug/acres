from acres.evaluation import evaluation


def test_analyze_file():
    (precision, recall) = evaluation.analyze_file("tests/resources/workbench.tsv")
    assert 0.0 == precision
    assert 0.0 == recall
