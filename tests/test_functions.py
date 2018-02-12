from .context import Functions
    
    
def test_splitNgram():    
    # Return empty if there's no acronym
    assert Functions.splitNgram("a b c") == []
    
    assert Functions.splitNgram("a AK b") == [('a', 'AK', 'b')]
    
    assert Functions.splitNgram("l ACR1 b ACR2 c") == [('l', 'ACR1', 'b ACR2 c'), ('l ACR1 b', 'ACR2', 'c')]
    
    assert Functions.splitNgram("ACR") == [('', 'ACR', '')]
    
    
def test_extractAcroDef():
    maxLength = 7;
    
    assert Functions.extractAcroDef("EKG (Elektrokardiogramm)", maxLength) == ('EKG', 'Elektrokardiogramm')
    assert Functions.extractAcroDef("Elektrokardiogramm (EKG)", maxLength) == ('EKG', 'Elektrokardiogramm')
    assert Functions.extractAcroDef("Elektrokardiogramm", maxLength) == None

    
def test_isAcronym():
    # Single digits are not acronyms
    assert Functions.isAcronym("A", 3) == False
    
    # Lower-case are not acronyms
    assert Functions.isAcronym("ecg", 3) == False
    assert Functions.isAcronym("Ecg", 3) == False
    
    # Double upper-case are acronyms
    assert Functions.isAcronym("AK", 2) == True
    
    # Acronyms should be shorter or equal to the maximum length
    assert Functions.isAcronym("EKG", 2) == False
    assert Functions.isAcronym("EKG", 3) == True
    
    # Acronyms can contain diacritics
    # XXX This fails with Python 2, because "Ä".isupper() == False
    assert Functions.isAcronym("ÄK", 3) == True
    
    # Acronyms can contain numbers
    assert Functions.isAcronym("5FU", 7) == True
    
    
def test_simplifyGermanString():
    assert Functions.simplifyGermanString("LEBER") == "leber"
    
    assert Functions.simplifyGermanString("ekg") == "ecg"
    assert Functions.simplifyGermanString("heißen") == "heissen"
    assert Functions.simplifyGermanString("Elektrokardiogramm") == "electrocardiogramm"
    
    # XXX Is it expected?
    assert Functions.simplifyGermanString("herz") == "herc"
    
    
def test_randomSubList():
    # We output the input list if the length requested is larger or equal to the input length 
    assert Functions.randomSubList(["a", "b"], 2) == ["a", "b"]
    assert Functions.randomSubList(["a", "b"], 3) == ["a", "b"]
    
    # TODO use Random.seed() so that the output is deterministic
    assert Functions.randomSubList(["a", "b"], 1) in [["a"], ["b"]]
    
    