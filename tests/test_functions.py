from .context import Functions
    
    
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
