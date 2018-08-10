import acres.util


def test_extract_acronym_definition():
    max_length = 7

    assert acres.util.acronym.extract_acronym_definition(
        "EKG (Elektrokardiogramm)", max_length) == ('EKG', 'Elektrokardiogramm')
    assert acres.util.acronym.extract_acronym_definition(
        "Elektrokardiogramm (EKG)", max_length) == ('EKG', 'Elektrokardiogramm')
    assert acres.util.acronym.extract_acronym_definition(
        "Elektrokardiogramm", max_length) is None
