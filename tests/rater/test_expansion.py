from acres.rater import expansion


def test__is_possible_expansion():
    # Baseline
    assert expansion._is_possible_expansion("EKG", "Elektrokardiogramm")

    # First char must match
    assert not expansion._is_possible_expansion("BC", "Abc")

    # Short acronyms
    assert expansion._is_possible_expansion("A", "a")
    assert expansion._is_possible_expansion("AB", "ab")

    # Invalid expansion
    assert not expansion._is_possible_expansion("EKG", "Elektro")

    # Equal last char
    assert expansion._is_possible_expansion("EKG", "Entwicklung")

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


def test__compute_expansion_valid():
    # Schwartz/Hearst criteria
    # FIXME Should be 1
    assert 5 == expansion._compute_expansion_valid("AE", "A b c d e")  # Short acronym
    assert 5 == expansion._compute_expansion_valid("ABCDEL", "A b c d e f g h i j k ll")  # Long acronym

    # RELATIVE LENGTH RESTRICTIONS
    # Acronym has to be at most 60% of the full form
    assert 2 == expansion._compute_expansion_valid("ABCE", "ABCDEF")
    # Full form can be up to 20 times longer than acronym
    assert 2 == expansion._compute_expansion_valid("AC", "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNO")

    # Levenshtein distance too high
    assert 4 == expansion._compute_expansion_valid("HEPA", "Ha Be Cp Dn Ean")

    # Acronym within full form
    assert 8 == expansion._compute_expansion_valid("AM", "AMbulanz")

    # Acronym characters not found in full form
    assert 16 == expansion._compute_expansion_valid("ECG", "Egramm")

    # Acronym tail on last word
    assert 32 == expansion._compute_expansion_valid("HEPC", "Hepacitis A")

    # XXX Uncommon expansions fail
    assert 20 == expansion._compute_expansion_valid("RR", "Blutdruck")
    assert 20 == expansion._compute_expansion_valid("EF", "Auswurffraktion")