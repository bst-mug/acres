from acres.rater import expansion


def test__is_possible_expansion():
    # Baseline
    assert expansion._is_possible_expansion("EKG", "Elektrokardiogramm")

    # First char must match
    assert not expansion._is_possible_expansion("BC", "Abc")

    # Short acronyms must match
    assert expansion._is_possible_expansion("A", "a")
    assert expansion._is_possible_expansion("AB", "ab")

    # Invalid expansion should not match
    assert not expansion._is_possible_expansion("EKG", "Elektro")

    # Equal last char should still match
    assert expansion._is_possible_expansion("EKG", "Entwicklung")

    # Wrong order shall not match
    assert not expansion._is_possible_expansion("EKG", "Entwigklun")   # sic

    # Extreme case should not match
    assert not expansion._is_possible_expansion("EKG", "Egggkkk")

    # Two same initial characters should still match
    assert expansion._is_possible_expansion("EKG", "Ekariogasas")

    # Second acronym char should not match first on expansion
    assert not expansion._is_possible_expansion("EEG", "Ekariogasas")

    # Empty parameters
    assert not expansion._is_possible_expansion("A", "")
    assert expansion._is_possible_expansion("", "a")
    assert expansion._is_possible_expansion("", "")


def test__is_acronym_tail_on_last_word():
    # Last char of acronym must occur in last word of full...
    assert not expansion._is_acronym_tail_on_last_word("HEPC", "Hepatitis Ab")
    assert expansion._is_acronym_tail_on_last_word("HEPA", "Hepatitis Ab")

    # ...but not at the end...
    assert not expansion._is_acronym_tail_on_last_word("HEPA", "Hepatitis Ba")

    # ...unless it is a single letter
    assert not expansion._is_acronym_tail_on_last_word("HEPC", "Hepacitis A")  # sic
    assert expansion._is_acronym_tail_on_last_word("HEPA", "Hepatitis A")


def test__is_expansion_initial_acronym():
    # Basic case
    assert not expansion._is_expansion_initial_acronym("TIA", "Transmuraler Myokardinfarkt")

    # Single word should still work
    assert expansion._is_expansion_initial_acronym("EKG", "Elektrokardiogramm")

    # Duplicate initials should also work
    assert expansion._is_expansion_initial_acronym("EEKKG", "Elektrokardiogramm")

    # Single last word should work
    assert expansion._is_expansion_initial_acronym("HEPA", "Hepatitis A")


def test__compute_expansion_valid():
    # Schwartz/Hearst criteria
    # FIXME Should be 1
    # assert 5 == expansion._compute_expansion_valid("AE", "A b c d e")  # Short acronym
    # assert 5 == expansion._compute_expansion_valid("ABCDEL", "A b c d e f g h i j k ll")  # Long acronym
    # assert 1 == expansion._compute_expansion_valid("AK", "auf die Substitution von Kalium")

    # RELATIVE LENGTH RESTRICTIONS
    # Acronym has to be at most 60% of the full form
    assert 2 == expansion._compute_expansion_valid("ABCE", "ABCDEF")
    # Full form can be up to 20 times longer than acronym
    assert 2 == expansion._compute_expansion_valid("AC", "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNO")

    assert 2 == expansion._compute_expansion_valid("RR", "Risikofaktorenmanagement insbesondere regelmäßige");

    # Levenshtein distance too high
    assert 4 == expansion._compute_expansion_valid("VB", "Vorgeschichte darf als bekannt")

    # Acronym within full form
    # assert 8 == expansion._compute_expansion_valid("AV", "AVBlock")

    # Acronym characters not found in full form
    assert 16 == expansion._compute_expansion_valid("MIN", "Implantation")

    # Acronym tail on last word
    assert 32 == expansion._compute_expansion_valid("AIN", "Ablation")

    # Acronym tail on last word
    assert 64 == expansion._compute_expansion_valid("TIA", "Transmuraler Myokardinfarkt")

    # XXX Uncommon expansions fail
    assert 20 == expansion._compute_expansion_valid("RR", "Blutdruck")
    assert 20 == expansion._compute_expansion_valid("EF", "Auswurffraktion")