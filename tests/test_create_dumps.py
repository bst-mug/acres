from acres import create_dumps


def test_create_morpho_dump():
    actual = create_dumps.create_morpho_dump("tests/resources/lex.xml", "tests/resources/lex.xml")
    expected = {'gramm', 'nieren', 'herc', 'crancheit', 'cardio', 'arbeits', 'el', 'cammer', 'electro', 'coronar'}

    assert expected.issubset(actual)
