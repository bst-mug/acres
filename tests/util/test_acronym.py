from acres.util import acronym


def test_is_acronym():
    # Single digits are not acronyms
    assert not acronym.is_acronym("A", 3)

    # Lower-case are not acronyms
    assert not acronym.is_acronym("ecg", 3)
    assert not acronym.is_acronym("Ecg", 3)

    # Double upper-case are acronyms
    assert acronym.is_acronym("AK", 2)

    # Acronyms should be shorter or equal to the maximum length
    assert not acronym.is_acronym("EKG", 2)
    assert acronym.is_acronym("EKG", 3)

    # Acronyms can contain diacritics
    # XXX This fails with Python 2, because "Ä".isupper() == False
    assert acronym.is_acronym("ÄK", 3)

    # Acronyms can contain numbers
    assert acronym.is_acronym("5FU", 7)

    # Hard, mixed cases due to variant generation...
    assert not acronym.is_acronym("VTEpisoden")
    assert not acronym.is_acronym("USdeme")


def test_create_german_acronym():
    # Baseline
    expected = "AP"
    actual = acronym.create_german_acronym("Angina pectoris")
    assert expected == actual

    # Separated by hyphen and whitespace
    expected = "WHB"
    actual = acronym.create_german_acronym("Wert - - Herzkrank-Board")
    assert expected == actual

    # Containing prepositions
    expected = "NIH"
    actual = acronym.create_german_acronym("National Institutes of Health")
    assert expected == actual

    # Expansion generated by find_embeddings
    expected = ""
    actual = acronym.create_german_acronym("-----------------")
    assert expected == actual

    # This fails.
    # TODO Reconsider some prepositions?
    # expected = "LCIS"
    # actual = acronym.create_german_acronym("lobular carcinoma in situ")
    # assert expected == actual


def test_trim_plural():
    # Baseline
    assert "EKG" == acronym.trim_plural("EKGs")
    assert "NT" == acronym.trim_plural("NTX")

    # Short forms should not be trimmed
    assert "SS" == acronym.trim_plural("SS")
    assert "TX" == acronym.trim_plural("TX")
    assert "DS" == acronym.trim_plural("DS")
    assert "US" == acronym.trim_plural("US")

    # XXX Some cases we still get wrong
    #assert "TRINS" == acronym.trim_plural("TRINS")
