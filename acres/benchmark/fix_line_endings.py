from acres.util import functions


def test_fine_ending_fixings():
    actual_input_text = """* Anamnese und klin. Symptomatik

Die Vorstellung des Pat. in der EBA für Innere Medizin
erfolgte aufgrund einer schmerzhaften Schwellung des li.
Oberschenkels. Eine Eigenanamnese ist mit dem Pat. nicht erhebbar. Laut
telef. Rücksprache mit dem Heim ist kein Sturz erhebbar.

* Physikalischer Status

Temp 36,3°, RR initial 198/90 nach 2 Hb Nitro 165,82
C: nc, arrh, leise
P iL bei < Compliance : VA
Abd.palp. unauff, lieg. PEG"""
    print(functions.fix_line_endings(actual_input_text, "\n"))
