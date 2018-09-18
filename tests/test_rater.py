from acres import rater


def test_get_acronym_score():
    assert 0 == rater.get_acronym_score("A", "Ambulanz")[1]  # Acronym too short
    assert 0 == rater.get_acronym_score("Aa", "Am")[1]  # Full form too short
    assert 0 == rater.get_acronym_score("AM", "AMbulanz")[1]  # Acronym within full form

    # Relative length do not match
    assert 0 == rater.get_acronym_score("AE", "a b c d e")[1]  # Short acronym
    assert 0 == rater.get_acronym_score("ABCDEL", "a b c d e f g h i j k ll")[1]  # Long acronym

    assert 0.2 == rater.get_acronym_score("NTX", "Nierentransplantation")[1]
    assert 2.0 == rater.get_acronym_score("TRINS", "Tricuspidalinsuffizienz")[1]
    assert 1.0 == rater.get_acronym_score("EKG", "Elektrokardiogramm")[1]
    assert 1.0 == rater.get_acronym_score("AK", "Arbeitskammer")[1]
    assert 1.0 == rater.get_acronym_score("KHK", "koronare Herzkrankheit")[1]

    assert 1.0 == rater.get_acronym_score("CMP", "Cardiomyopathie")[1]
