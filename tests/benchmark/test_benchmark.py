import pytest

from acres import constants
from acres.evaluation import evaluation
from acres.ngram import finder
from acres.preprocess import resource_factory
from acres.resolution import resolver
from acres.util import text


def test_fixture():
    assert "tests" not in resource_factory.PICKLE_FOLDER


def test_fix_line_endings():
    doc = """* Anamnese und klin. Symptomatik

Die Vorstellung des Pat. in der EBA für Innere Medizin
erfolgte aufgrund einer schmerzhaften Schwellung des li.
Oberschenkels. Eine Eigenanamnese ist mit dem Pat. nicht erhebbar. Laut
telef. Rücksprache mit dem Heim ist kein Sturz erhebbar.

* Physikalischer Status

Temp 36,3°, RR initial 198/90 nach 2 Hb Nitro 165,82
C: nc, arrh, leise
P iL bei < Compliance : VA
Abd.palp. unauff, lieg. PEG"""

    expected = """* Anamnese und klin. Symptomatik

Die Vorstellung des Pat. in der EBA für Innere Medizin erfolgte aufgrund einer schmerzhaften Schwellung des li. Oberschenkels. Eine Eigenanamnese ist mit dem Pat. nicht erhebbar. Laut telef. Rücksprache mit dem Heim ist kein Sturz erhebbar.

* Physikalischer Status

Temp 36,3°, RR initial 198/90 nach 2 Hb Nitro 165,82
C: nc, arrh, leise
P iL bei < Compliance : VA
Abd.palp. unauff, lieg. PEG
"""

    # Save and restore line_break
    old_line_break = constants.LINE_BREAK
    constants.LINE_BREAK = "\n"

    actual = text.fix_line_endings(doc)

    constants.LINE_BREAK = old_line_break

    assert expected == actual


def test_find_embeddings():
    finder_constraints = finder.FinderConstraints(min_freq=2, max_count=500, min_num_tokens=1,
                                                  max_num_tokens=10)
    actual = finder.find_embeddings("nach", "ICD", "Implantation", finder_constraints)
    expected = [(273, 'CRT ICD'), (221, 'prophylaktischer CRT ICD'), (257, 'prophylaktischer ICD')]
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("<SEL>", "HF-Anstieg", "von", finder_constraints)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("<SEL>", "HT", "rein", finder_constraints)
    expected = []
    assert set(expected).issubset(actual)

    # viele Treffer, die mit Ht anfangen
    actual = finder.find_embeddings("geplanten", "EPU", "*", finder_constraints)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("einem", "EDP", "von", finder_constraints)
    expected = [(1741, 'max Gradienten'), (710, 'mittleren Gradienten'), (325, 'LVEDD')]
    assert set(expected).issubset(actual)

    # wird nicht gefunden
    stricter_max_count = finder.FinderConstraints(min_freq=2, max_count=100, min_num_tokens=1,
                                                  max_num_tokens=10)
    actual = finder.find_embeddings("gutem", "AZ", "nach", stricter_max_count)
    expected = [(312, 'AZ und mit blander Punktionsstelle'), (277, 'AZ wieder'),
                (141, 'AZ und bei blander Punktionsstelle')]
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("die", "VCS.", "<SEL>", finder_constraints)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("<SEL>", "DG's", "<SEL>", finder_constraints)
    expected = []
    assert set(expected).issubset(actual)

    # only without restricted context the resolution is found
    # only DG's resolved, not DGs
    actual = finder.find_embeddings("die", "VCS.", "<SEL>", finder_constraints)
    expected = []
    assert set(expected).issubset(actual)

    # only works with final dot!
    actual = finder.find_embeddings("re", "OL", "<SEL>", finder_constraints)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("die", "VCS", "<VOID>",
                                    finder.FinderConstraints(min_freq=1, max_count=100,
                                                             min_num_tokens=1, max_num_tokens=10))
    expected = []
    assert set(expected).issubset(actual)

    # Code originally commented out below #

    actual = finder.find_embeddings("", "morph.", "",
                                    finder.FinderConstraints(min_freq=3, max_count=1000,
                                                             min_num_tokens=1, max_num_tokens=7))
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("Mitralklappe", "morph.", "*",
                                    finder.FinderConstraints(min_freq=3, max_count=1000,
                                                             min_num_tokens=1, max_num_tokens=7))
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("", "morph.", "",
                                    finder.FinderConstraints(min_freq=3, max_count=1000,
                                                             min_num_tokens=1, max_num_tokens=1))
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("", "morph.", "unauff.",
                                    finder.FinderConstraints(min_freq=3, max_count=1000,
                                                             min_num_tokens=3, max_num_tokens=7))
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("<SEL>", "ms", "<SEL>",
                                    finder.FinderConstraints(min_freq=30, max_count=500,
                                                             min_num_tokens=1, max_num_tokens=5))
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("Ð,Ð", "ms", "",
                                    finder.FinderConstraints(min_freq=3, max_count=500,
                                                             min_num_tokens=1, max_num_tokens=7))
    expected = []
    assert set(expected).issubset(actual)


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
    (precision, recall) = evaluation.do_analysis("resources/stefan_topic_list.tsv",
                                                 "resources/detection_standard.tsv",
                                                 "resources/expansion_standard.tsv",
                                                 resolver.Strategy.WORD2VEC, evaluation.Level.TYPE,
                                                 10, True)
    absolute_tolerance = 0.02
    assert precision == pytest.approx(0.85, abs=absolute_tolerance)
    assert recall == pytest.approx(0.72, abs=absolute_tolerance)

    (precision, recall) = evaluation.do_analysis("resources/stefan_topic_list.tsv",
                                                 "resources/detection_standard.tsv",
                                                 "resources/expansion_standard.tsv",
                                                 resolver.Strategy.DICTIONARY,
                                                 evaluation.Level.TYPE,
                                                 10, True)
    absolute_tolerance = 0.02
    assert precision == pytest.approx(0.68, abs=absolute_tolerance)
    assert recall == pytest.approx(0.42, abs=absolute_tolerance)
