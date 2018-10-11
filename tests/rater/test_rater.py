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

    # Short acronyms ending with X are not allowed
    assert 0 == rater.get_acronym_score("TX", "Transplantation")

    # TODO Wrong
    #assert rater.get_acronym_score("SR", "Sinusrythmus") > rater.get_acronym_score("SR", "Sinusarrhythmie")


def test_get_acronym_score_variants():
    # Acronyms created out of spelling variants are accepted
    assert 1.0 == rater.get_acronym_score_variants("AK", "Arbeitskammer")
    assert 1.0 == rater.get_acronym_score_variants("AC", "Arbeitskammer")

    # But not the opposite!
    # TODO Is is expected?
    assert 0.0 == rater.get_acronym_score_variants("AK", "Arbeitscammer")

    # Score of the best variant should be preserved
    assert 2.0 == rater.get_acronym_score_variants("AK", "Arbeits Kranker")    # sic

    # Acronyms with only plural letters should not cause IndexError
    assert 0 == rater.get_acronym_score_variants("SS", "Überprüfen Sie die")


def test_get_acronym_definition_pair_score():
    assert 10 == rater.get_acro_def_pair_score("EKG", "EKG (Elektrokardiogramm)")[1]

    # FIXME Does not work
    #assert 10 == rater.get_acronym_definition_pair_score("ARDS", "ARDS (akutes Atemnotsyndrom)")[1]