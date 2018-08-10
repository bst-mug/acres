import acres.util


def test_extract_acronym_definition():
    max_length = 7

    assert acres.util.acronym.extract_acronym_definition(
        "EKG (Elektrokardiogramm)", max_length) == ('EKG', 'Elektrokardiogramm')
    assert acres.util.acronym.extract_acronym_definition(
        "Elektrokardiogramm (EKG)", max_length) == ('EKG', 'Elektrokardiogramm')
    assert acres.util.acronym.extract_acronym_definition(
        "Elektrokardiogramm", max_length) is None


def test_is_acronym():
    # Single digits are not acronyms
    assert not acres.util.acronym.is_acronym("A", 3)

    # Lower-case are not acronyms
    assert not acres.util.acronym.is_acronym("ecg", 3)
    assert not acres.util.acronym.is_acronym("Ecg", 3)

    # Double upper-case are acronyms
    assert acres.util.acronym.is_acronym("AK", 2)

    # Acronyms should be shorter or equal to the maximum length
    assert not acres.util.acronym.is_acronym("EKG", 2)
    assert acres.util.acronym.is_acronym("EKG", 3)

    # Acronyms can contain diacritics
    # XXX This fails with Python 2, because "Ä".isupper() == False
    assert acres.util.acronym.is_acronym("ÄK", 3)

    # Acronyms can contain numbers
    assert acres.util.acronym.is_acronym("5FU", 7)


def test_find_acronym_expansion():
    assert [] == acres.util.acronym.find_acro_expansions([])

    # FIXME explain reasoning and fix possible bugs
    expected = ['Im normale EKG post50     Im normalen elektrokardiogramm post30']
    actual = acres.util.acronym.find_acro_expansions(["50\tIm normale EKG post",
                                                      "30\tIm normalen elektrokardiogramm post"])
    assert expected == actual


def test_split_expansion():
    # Baseline
    expected = [('Elektro', 'kardio', 'gramm'),
                ('Ele', 'ktrokardio', 'gramm')]
    actual = acres.util.acronym.split_expansion("EKG", "Elektrokardiogramm")
    assert expected == actual

    # Single letter acronyms, even though not valid, should not break
    expected = [('a')]
    actual = acres.util.acronym.split_expansion("A", "a")
    assert expected == actual

    # Expansion = acronym should still work
    expected = [('a', 'b')]
    actual = acres.util.acronym.split_expansion("AB", "ab")
    assert expected == actual

    expected = [('a', 'b', 'c')]
    actual = acres.util.acronym.split_expansion("ABC", "abc")
    assert expected == actual

    expected = [('a', 'b', 'c', 'd', 'e')]
    actual = acres.util.acronym.split_expansion("ABCDE", "abcde")
    assert expected == actual

    # Unexpected splits
    expected = [('T', 'rikuspidal', 'i', 'n', 'suffizienz'),  # Correct one
                ('T', 'r', 'ikuspidali', 'n', 'suffizienz')]
    actual = acres.util.acronym.split_expansion("TRINS", "Trikuspidalinsuffizienz")
    assert expected == actual

    # No valid expansion should return empty
    expected = []
    actual = acres.util.acronym.split_expansion("EKG", "Elektro")
    assert expected == actual


def test__acronym_aware_clean_expansion():
    # Baseline: return expansion if no symbols are found
    assert "Elektrokardiogramm" == acres.util.acronym._acronym_aware_clean_expansion("EKG",
                                                                                     "Elektrokardiogramm")

    # We should clean symbols, unless they appear in the acronym itself
    assert "Angina pectoris" == acres.util.acronym._acronym_aware_clean_expansion("AP",
                                                                                  "Angina&pectoris")
    assert "Angina&pectoris" == acres.util.acronym._acronym_aware_clean_expansion("A&P",
                                                                                  "Angina&pectoris")

    # We should preserve spaces, happening or not in the acronym itself
    assert "Angina pectoris" == acres.util.acronym._acronym_aware_clean_expansion("AP",
                                                                                  "Angina pectoris")
    assert "Angina pectoris" == acres.util.acronym._acronym_aware_clean_expansion("A P",
                                                                                  "Angina pectoris")

    # We should preserve hyphens, happening or not in the acronym itself
    assert "Angina-pectoris" == acres.util.acronym._acronym_aware_clean_expansion("AP",
                                                                                  "Angina-pectoris")
    assert "Angina-pectoris" == acres.util.acronym._acronym_aware_clean_expansion("A-P",
                                                                                  "Angina-pectoris")

    # We strip the output even if the acronym itself is stripped
    assert "Angina pectoris" == acres.util.acronym._acronym_aware_clean_expansion(" AP ",
                                                                                  " Angina pectoris ")

    # XXX We do not remove duplicated spaces
    assert "Angina   pectoris" == acres.util.acronym._acronym_aware_clean_expansion("AP",
                                                                                    "Angina&&&pectoris")


def test_split_ngram():
    # pass
    assert acres.util.acronym.split_ngram("a b c") == []
    #
    assert acres.util.acronym.split_ngram("a AK b") == [('a', 'AK', 'b')]
    #
    assert acres.util.acronym.split_ngram("l ACR1 b ACR2 c") == [(
        'l', 'ACR1', 'b ACR2 c'), ('l ACR1 b', 'ACR2', 'c')]
    #
    assert acres.util.acronym.split_ngram("ACR") == [('', 'ACR', '')]
