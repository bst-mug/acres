from acres.util import variants


def test__resolve_ambiguous_lists():
    expected = [['cyclophospham', ('id', 'ide')], ['cyclophospham', 'id'], ['cyclophospham', 'ide']]
    actual = variants._resolve_ambiguous_lists([['cyclophospham', ('id', 'ide')]])
    assert expected == actual


def test__create_string_variants_as_list():
    expected = ['cyclophospham', ('id', 'ide')]
    actual = variants._create_string_variants_as_list("cyclophosphamid", "id", "ide")
    assert expected == actual

    # Empty search returns the imput string as a list
    expected = ['cyclophosphamid']
    actual = variants._create_string_variants_as_list("cyclophosphamid", "", "ide")
    assert expected == actual


def test__list_to_string():
    expected = "abc"
    actual = variants._list_to_string(["a", "b", "c"])
    assert expected == actual

    # Non-string element returns empty
    expected = ""
    actual = variants._list_to_string(["a", "b", "c", ("g", "e")])
    assert expected == actual


def test__list_all_string_variants():
    expected = ['cyclophosphamid', 'cyclophosphamide']
    actual = variants._list_all_string_variants("cyclophosphamid", "id", "ide")
    assert expected == actual


def test_generate_all_variants_by_rules():
    expected = ['Arterielle Verschlusskrankheit', 'Arterielle Verschluss Disorder',
                'Arterielle Verschlusscrankheit']
    actual = variants.generate_all_variants_by_rules("Arterielle Verschlusskrankheit")
    assert expected == actual

    expected = ["elektrokardiogramm", "elektrocardiogramm"]
    assert expected == variants.generate_all_variants_by_rules("elektrokardiogramm")

    # TODO "esophagus" is never mentioned in the corpus, while "oesophagus" is.
    #assert ["ösophagus", "oesophagus"] == variants.generate_all_variants_by_rules("ösophagus")
    assert ["herz"] == variants.generate_all_variants_by_rules("herz")
    assert ["café"] == variants.generate_all_variants_by_rules("café")  # TODO add cafe
    assert ["à"] == variants.generate_all_variants_by_rules("à")        # TODO add a
