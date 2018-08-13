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
