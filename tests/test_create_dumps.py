import os.path

from acres import create_dumps


def test_create_morpho_dump():
    output_file = "tests/models/pickle/morphemes.p"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    create_dumps.create_morpho_dump("tests/resources/lex.xml", "tests/resources/lex.xml", True)
    assert os.path.isfile(output_file)
