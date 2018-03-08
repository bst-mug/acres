from acres.rate_acronym_resolutions import get_acronym_score


def test_get_acronym_score():
    assert get_acronym_score("A", "Ambulanz", True) == 0  # Acronym too short
    assert get_acronym_score("Aa", "Am", True) == 0  # Full form too short
    assert get_acronym_score("AM", "AMbulanz", True) == 0  # Acronym within full form

    # Relative length do not match
    assert get_acronym_score("AE", "a b c d e", True) == 0  # Short acronym
    assert get_acronym_score("ABCDEL", "a b c d e f g h i j k ll", True) == 0  # Long acronym

    assert get_acronym_score("NTX", "Nierentransplantation", True) == 0.5
    assert get_acronym_score("TRINS", "Tricuspidalinsuffizienz", True) == 0.5
    assert get_acronym_score("EKG", "Elektrokardiogramm", True) == 1.0
    assert get_acronym_score("AK", "Arbeitskammer", True) == 1.0
    assert get_acronym_score("KHK", "koronare Herzkrankheit", True) == 1.0
