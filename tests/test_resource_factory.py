from acres import resource_factory


def test_get_morphemes():
    actual = resource_factory.get_morphemes()
    expected = {'gramm', 'nieren', 'herc', 'crancheit', 'cardio', 'arbeits', 'el', 'cammer', 'electro', 'coronar'}

    assert expected.issubset(actual)
