from acres.rater import rater


def test__calc_score():
    # Baseline
    assert 1.0 == rater._calc_score("EKG", "Elektrokardiogramm")
    assert 1.0 == rater._calc_score("KHK", "koronare Herzkrankheit")
    assert 1.0 == rater._calc_score("CMP", "Cardiomyopathie")

    # Lower case rightmost expansion is penalized
    assert 0.25 == rater._calc_score("AP", "Angina leptoris")

    # Short full form with same initial letters gets a boost
    assert 2.0 == rater._calc_score("TRINS", "Tricuspidalinsuffizienz")

    # Exact match of acronym to generated acronym
    assert 2.0 == rater._calc_score("AP", "Angina Pectoris")

    # Acronym as a substring of full form (case-insensitive) is penalized
    assert 0.2 == rater._calc_score("NT", "Nierentransplantation")


def test_get_acronym_score():
    # BASIC CHECKS
    # Acronym too short
    assert 0 == rater.get_acronym_score("A", "Ambulanz")

    # Invalid full form
    assert 0 == rater.get_acronym_score("A", "Auf Abcde(fghi")

    # PLURAL FORMS
    # Plural form in English format
    assert 1 == rater.get_acronym_score("EKGs", "Elektrokardiogramme")

    # Final X is not needed in full form
    assert 0.2 == rater.get_acronym_score("NTX", "Nierentransplantation")

    # ...unless it's a short acronym
    assert 1 == rater.get_acronym_score("DS", "Druckschmerz")

    # TODO Short acronyms ending with X or S are not allowed
    #assert 0 < rater.get_acronym_score("TX", "Transplantation")

    # TODO Wrong
    #assert rater.get_acronym_score("SR", "Sinusrythmus") > rater.get_acronym_score("SR", "Sinusarrhythmie")
