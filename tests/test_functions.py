from .context import functions


def test_splitNgram():
    # Return empty if there's no acronym
    assert functions.splitNgram("a b c") == []

    assert functions.splitNgram("a AK b") == [('a', 'AK', 'b')]

    assert functions.splitNgram("l ACR1 b ACR2 c") == [('l', 'ACR1', 'b ACR2 c'), ('l ACR1 b', 'ACR2', 'c')]

    assert functions.splitNgram("ACR") == [('', 'ACR', '')]


def test_extractAcroDef():
    maxLength = 7

    assert functions.extractAcroDef("EKG (Elektrokardiogramm)", maxLength) == ('EKG', 'Elektrokardiogramm')
    assert functions.extractAcroDef("Elektrokardiogramm (EKG)", maxLength) == ('EKG', 'Elektrokardiogramm')
    assert functions.extractAcroDef("Elektrokardiogramm", maxLength) == None


def test_isAcronym():
    # Single digits are not acronyms
    assert functions.isAcronym("A", 3) == False

    # Lower-case are not acronyms
    assert functions.isAcronym("ecg", 3) == False
    assert functions.isAcronym("Ecg", 3) == False

    # Double upper-case are acronyms
    assert functions.isAcronym("AK", 2) == True

    # Acronyms should be shorter or equal to the maximum length
    assert functions.isAcronym("EKG", 2) == False
    assert functions.isAcronym("EKG", 3) == True

    # Acronyms can contain diacritics
    # XXX This fails with Python 2, because "Ä".isupper() == False
    assert functions.isAcronym("ÄK", 3) == True

    # Acronyms can contain numbers
    assert functions.isAcronym("5FU", 7) == True


def test_simplifyGermanString():
    assert functions.simplifyGermanString("LEBER") == "leber"

    assert functions.simplifyGermanString("ekg") == "ecg"
    assert functions.simplifyGermanString("heißen") == "heissen"
    assert functions.simplifyGermanString("Elektrokardiogramm") == "electrocardiogramm"

    # XXX Is it expected?
    assert functions.simplifyGermanString("herz") == "herc"

    assert functions.simplifyGermanString("café") == "cafe"


def test_randomSubList():
    # We output the input list if the length requested is larger or equal to the input length 
    assert functions.randomSubList(["a", "b"], 2) == ["a", "b"]
    assert functions.randomSubList(["a", "b"], 3) == ["a", "b"]

    # TODO use Random.seed() so that the output is deterministic
    assert functions.randomSubList(["a", "b"], 1) in [["a"], ["b"]]
