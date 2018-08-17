from acres.rater import get_acronym_score


def test_get_acronym_score():
    assert get_acronym_score("A", "Ambulanz")[1] == 0  # Acronym too short
    assert get_acronym_score("Aa", "Am")[1] == 0  # Full form too short
    assert get_acronym_score("AM", "AMbulanz")[1] == 0  # Acronym within full form

    # Relative length do not match
    assert get_acronym_score("AE", "a b c d e")[1] == 0  # Short acronym
    assert get_acronym_score("ABCDEL", "a b c d e f g h i j k ll")[1] == 0  # Long acronym

    assert get_acronym_score("NTX", "Nierentransplantation")[1] == 0.5
    assert get_acronym_score("TRINS", "Tricuspidalinsuffizienz")[1] == 0.5
    assert get_acronym_score("EKG", "Elektrokardiogramm")[1] == 1.0
    assert get_acronym_score("AK", "Arbeitskammer")[1] == 1.0
    assert get_acronym_score("KHK", "koronare Herzkrankheit")[1] == 1.0
