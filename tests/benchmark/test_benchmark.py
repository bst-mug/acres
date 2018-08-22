from acres.ngram import finder
from acres.preprocess import create_dumps
from acres.preprocess import resource_factory
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

    actual = text.fix_line_endings(doc, "\n")
    assert expected == actual


def test_find_embeddings():
    actual = finder.find_embeddings("nach", "ICD", "Implantation", 1, 2, 500, 1, 10)
    expected = [(76, 'CRT/ICD'), (50, 'prophylaktischer CRT/ICD'), (42, 'prophylaktischer ICD')]
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("<SEL>", "HF-Anstieg", "von", 1, 2, 500, 1, 10)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("<SEL>", "HT", "rein", 1, 2, 500, 1, 10)
    expected = []
    assert set(expected).issubset(actual)

    # viele Treffer, die mit Ht anfangen
    actual = finder.find_embeddings("geplanten", "EPU", "*", 1, 2, 500, 1, 10)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("einem", "EDP", "von", 1, 2, 500, 1, 10)
    expected = [(1737, 'max. Gradienten'), (710, 'mittleren Gradienten'), (325, 'LVEDD')]
    assert set(expected).issubset(actual)

    # wird nicht gefunden
    actual = finder.find_embeddings("gutem", "AZ", "nach", 1, 2, 100, 1, 10)
    expected = [(311, 'AZ und mit blander Punktionsstelle'), (277, 'AZ wieder'),
                (140, 'AZ und bei blander Punktionsstelle')]
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("die", "VCS.", "<SEL>", 1, 2, 500, 1, 10)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("<SEL>", "DG's", "<SEL>", 1, 2, 500, 1, 10)
    expected = []
    assert set(expected).issubset(actual)

    # only without restricted context the resolution is found
    # only DG's resolved, not DGs
    actual = finder.find_embeddings("die", "VCS.", "<SEL>", 1, 2, 500, 1, 10)
    expected = []
    assert set(expected).issubset(actual)

    # only works with final dot!
    actual = finder.find_embeddings("re", "OL", "<SEL>", 1, 2, 500, 1, 10)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("die", "VCS", "<VOID>", 3, 1, 100, 1, 10)
    expected = []
    assert set(expected).issubset(actual)

    # Code originally commented out below #

    actual = finder.find_embeddings("", "morph.", "", 10, 3, 1000, 1, 7)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("Mitralklappe", "morph.", "*", 10, 3, 1000, 1, 7)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("", "morph.", "", 18, 3, 1000, 1, 1)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("", "morph.", "unauff.", 18, 3, 1000, 3, 7)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("<SEL>", "ms", "<SEL>", 8, 30, 500, 1, 5)
    expected = []
    assert set(expected).issubset(actual)

    actual = finder.find_embeddings("Ð,Ð", "ms", "", 8, 3, 500, 1, 7)
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
