from .context import Functions
    
    
def test_isAcronym():
    # Single digits are not acronyms
    assert Functions.isAcronym("A", 3) == False
    
    # Acronyms should be shorter than the maximum length
    assert Functions.isAcronym("EKG", 2) == False
    assert Functions.isAcronym("EKG", 3) == True
    
    # Acronyms can contain diacritics
    # XXX This fails with Python 2, because "Ä".isupper() == False
    assert Functions.isAcronym("ÄK", 3) == True
    
    # Acronyms can contain numbers
    assert Functions.isAcronym("5FU", 7) == True
