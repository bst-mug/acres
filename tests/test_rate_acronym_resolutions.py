from acres.rate_acronym_resolutions import get_acronym_score


def test_get_acronym_score():
    assert get_acronym_score("A", "Ambulanz") == 0  # Acronym too short
    assert get_acronym_score("Aa", "Am") == 0  # Full form too short
    assert get_acronym_score("AM", "AMbulanz") == 0  # Acronym within full form

    # Relative length do not match
    assert get_acronym_score("AE", "a b c d e") == 0  # Short acronym
    assert get_acronym_score("ABCDEL", "a b c d e f g h i j k ll") == 0  # Long acronym

    assert get_acronym_score("NTX", "Nierentransplantation") == 0.125
    assert get_acronym_score("TRINS", "Tricuspidalinsuffizienz") == 0.15
    assert get_acronym_score("EKG", "Elektrokardiogramm") >= 0.166
    assert get_acronym_score("AK", "Arbeitskammer") == 0.25
    assert get_acronym_score("KHK", "koronare Herzkrankheit") == 0.25
