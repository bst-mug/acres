import pytest

from acres.evaluation import evaluation, metrics
from acres.preprocess import resource_factory
from acres.resolution import resolver


def test_fixture():
    assert "tests" not in resource_factory.PICKLE_FOLDER


def test_get_word_ngrams():
    ngrams = resource_factory.get_word_ngrams().keys()
    unique_ngrams = set(ngrams)

    # ngramstat should not have empty entries
    assert "" not in unique_ngrams
    assert " " not in unique_ngrams

    # ngramstat should not have duplicate entries
    assert len(unique_ngrams) == len(ngrams)


def test_evaluation():
    # XXX word2vec is not deterministic, different models might lead to slighthly different metrics
    correct, found, valid = evaluation.do_analysis("resources/stefan_topic_list.tsv",
                                                 "resources/detection_standard.tsv",
                                                 "resources/expansion_standard.tsv",
                                                 resolver.Strategy.WORD2VEC, evaluation.Level.TYPE,
                                                 10, True)
    precision = metrics.calculate_precision(len(correct), len(found))
    recall = metrics.calculate_recall(len(correct), len(valid))

    absolute_tolerance = 0.02
    assert pytest.approx(0.81, abs=absolute_tolerance) == precision
    assert pytest.approx(0.68, abs=absolute_tolerance) == recall

    correct, found, valid = evaluation.do_analysis("resources/stefan_topic_list.tsv",
                                                 "resources/detection_standard.tsv",
                                                 "resources/expansion_standard.tsv",
                                                 resolver.Strategy.DICTIONARY,
                                                 evaluation.Level.TYPE,
                                                 10, True)
    precision = metrics.calculate_precision(len(correct), len(found))
    recall = metrics.calculate_recall(len(correct), len(valid))

    absolute_tolerance = 0.02
    assert pytest.approx(0.81, abs=absolute_tolerance) == precision
    assert pytest.approx(0.49, abs=absolute_tolerance) == recall
