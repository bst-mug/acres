import os.path

from acres import resource_factory


def test_get_morphemes():
    output_file = "tests/models/pickle/morphemes.p"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    resource_factory.get_morphemes()
    assert os.path.isfile(output_file)


def test_get_ngramstart():
    output_file = "tests/models/pickle/ngramstat.p"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    resource_factory.get_ngramstat()
    assert os.path.isfile(output_file)


def test_get_character_ngrams():
    output_file = "tests/models/pickle/character_ngrams.p"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    resource_factory.get_character_ngrams()
    assert os.path.isfile(output_file)
