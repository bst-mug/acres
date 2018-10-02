from acres import rater


def test__compute_full_valid():
    # Full form has parenthesis
    assert 1 == rater._compute_full_valid("Abcde(fghi")

    # Full form too short
    assert 2 == rater._compute_full_valid("As")

    # Full form starts with stopword
    assert 4 == rater._compute_full_valid("Auf das")

    # Full form has no capitals
    assert 8 == rater._compute_full_valid("ambulanz")


def test__compute_expansion_valid():
    # Schwartz/Hearst criteria
    # FIXME Should be 1
    assert 5 == rater._compute_expansion_valid("AE", "A b c d e")  # Short acronym
    assert 5 == rater._compute_expansion_valid("ABCDEL", "A b c d e f g h i j k ll")  # Long acronym

    # RELATIVE LENGTH RESTRICTIONS
    # Acronym has to be at most 60% of the full form
    assert 2 == rater._compute_expansion_valid("DCBA", "ABCDEF")
    # Full form can be up to 20 times longer than acronym
    assert 2 == rater._compute_expansion_valid("BA", "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNO")

    # Levenshtein distance too high
    assert 4 == rater._compute_expansion_valid("HEPA", "A B C D")

    # Acronym within full form
    assert 8 == rater._compute_expansion_valid("AM", "AMbulanz")


def test_get_acronym_score():
    # BASIC CHECKS
    # Acronym too short
    assert 0 == rater.get_acronym_score("A", "Ambulanz")

    # Rightmost acronym character is not in rightmost word
    assert 0 == rater.get_acronym_score("CK", "Creaking Test")

    # Acronym characters not found in full form
    assert 0 == rater.get_acronym_score("ECG", "Egramm")

    # Baseline
    assert 1.0 == rater.get_acronym_score("EKG", "Elektrokardiogramm")
    assert 1.0 == rater.get_acronym_score("KHK", "koronare Herzkrankheit")
    assert 1.0 == rater.get_acronym_score("CMP", "Cardiomyopathie")

    # Lower case rightmost expansion is penalized
    assert 0.25 == rater.get_acronym_score("AP", "Angina leptoris")

    # Acronym as a substring of full form (case-insensitive) is penalized
    assert 0.2 == rater.get_acronym_score("NTX", "Nierentransplantation")

    # Short full form with same initial letters gets a boost
    assert 2.0 == rater.get_acronym_score("TRINS", "Tricuspidalinsuffizienz")

    # Exact match of acronym to generated acronym
    assert 2.0 == rater.get_acronym_score("AP", "Angina Pectoris")

    # Acronyms created out of spelling variants are accepted
    assert 1.0 == rater.get_acronym_score("AK", "Arbeitskammer")
    assert 1.0 == rater.get_acronym_score("AC", "Arbeitskammer")

    # But not the opposite!
    # TODO Is is expected?
    assert 0.0 == rater.get_acronym_score("AK", "Arbeitscammer")

    # Score of the best variant should be preserved
    assert 2.0 == rater.get_acronym_score("AK", "Arbeits Kranker")    # sic

    # Acronyms with only plural letters should not cause IndexError
    assert 0 == rater.get_acronym_score("SS", "Überprüfen Sie die")

    # TODO Wrong
    #assert rater.get_acronym_score("SR", "Sinusrythmus") > rater.get_acronym_score("SR", "Sinusarrhythmie")
