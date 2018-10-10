from acres.rater import full


def test__compute_full_valid():
    # Full form has parenthesis
    assert 1 == full._compute_full_valid("Abcde(fghi")

    # Full form too short
    assert 2 == full._compute_full_valid("As")

    # Full form starts with stopword
    assert 4 == full._compute_full_valid("Auf das")

    # Full form has no capitals
    assert 8 == full._compute_full_valid("ambulanz")