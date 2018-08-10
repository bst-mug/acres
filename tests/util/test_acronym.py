import acres.util


def test_extract_acronym_definition():
    max_length = 7

    assert acres.util.acronym.extract_acronym_definition(
        "EKG (Elektrokardiogramm)", max_length) == ('EKG', 'Elektrokardiogramm')
    assert acres.util.acronym.extract_acronym_definition(
        "Elektrokardiogramm (EKG)", max_length) == ('EKG', 'Elektrokardiogramm')
    assert acres.util.acronym.extract_acronym_definition(
        "Elektrokardiogramm", max_length) is None


def test_is_acronym():
    # Single digits are not acronyms
    assert not acres.util.acronym.is_acronym("A", 3)

    # Lower-case are not acronyms
    assert not acres.util.acronym.is_acronym("ecg", 3)
    assert not acres.util.acronym.is_acronym("Ecg", 3)

    # Double upper-case are acronyms
    assert acres.util.acronym.is_acronym("AK", 2)

    # Acronyms should be shorter or equal to the maximum length
    assert not acres.util.acronym.is_acronym("EKG", 2)
    assert acres.util.acronym.is_acronym("EKG", 3)

    # Acronyms can contain diacritics
    # XXX This fails with Python 2, because "Ä".isupper() == False
    assert acres.util.acronym.is_acronym("ÄK", 3)

    # Acronyms can contain numbers
    assert acres.util.acronym.is_acronym("5FU", 7)
