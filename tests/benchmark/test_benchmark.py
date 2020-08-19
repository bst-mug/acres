import pytest

from acres import constants
from acres.evaluation import evaluation
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
    assert precision == pytest.approx(0.81, abs=absolute_tolerance)
    assert recall == pytest.approx(0.68, abs=absolute_tolerance)

    (precision, recall) = evaluation.do_analysis("resources/stefan_topic_list.tsv",
                                                 "resources/detection_standard.tsv",
                                                 "resources/expansion_standard.tsv",
                                                 resolver.Strategy.DICTIONARY,
                                                 evaluation.Level.TYPE,
                                                 10, True)
    absolute_tolerance = 0.02
    assert precision == pytest.approx(0.81, abs=absolute_tolerance)
    assert recall == pytest.approx(0.49, abs=absolute_tolerance)
