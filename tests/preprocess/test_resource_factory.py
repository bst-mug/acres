import os.path

from acres.preprocess import resource_factory
from acres.preprocess import create_dumps


def test_fixture():
    assert "tests" in resource_factory.PICKLE_FOLDER


def test_get_morphemes():
    output_file = "tests/models/pickle/morphemes.p"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    # Forces recreation
    resource_factory.MORPHEMES = []

    resource_factory.get_morphemes()
    assert os.path.isfile(output_file)


def test_getindex(ngramstat):
    resource_factory.MIN_FREQ = 1

    output_file = "tests/models/pickle/index-1-" + resource_factory.VERSION + ".p"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    # Forces recreation
    resource_factory.INDEX = []

    resource_factory.get_index()
    assert os.path.isfile(output_file)


def test_get_ngramstat(monkeypatch, ngramstat):
    # Monkey patch create_indexed_ngrams so that it returns the fake ngramstat
    def mockreturn(word_ngrams):
        return ngramstat
    monkeypatch.setattr(create_dumps, "create_indexed_ngrams", mockreturn)

    resource_factory.MIN_FREQ = 1
    
    output_file = "tests/models/pickle/ngramstat-1-" + resource_factory.VERSION + ".p"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    # Forces recreation
    resource_factory.NGRAMSTAT = []

    resource_factory.get_ngramstat()
    assert os.path.isfile(output_file)


def test_get_acronym_ngrams(monkeypatch):
    # Monkey patch create_new_acro_dump so that tests do not depend on all acronyms
    def mockreturn():
        return ["EKG", "AP"]
    monkeypatch.setattr(create_dumps, "create_new_acro_dump", mockreturn)

    output_file = "tests/models/pickle/acronymNgrams.p"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    resource_factory.get_acronym_ngrams()
    assert os.path.isfile(output_file)


def test_get_acronyms():
    output_file = "tests/models/pickle/acronyms.p"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    resource_factory.get_acronyms()
    assert os.path.isfile(output_file)


def test_get_character_ngrams():
    output_file = "tests/models/pickle/character_ngrams.p"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    # Forces recreation
    resource_factory.CHARACTER_NGRAMS = {}

    resource_factory.get_character_ngrams()
    assert os.path.isfile(output_file)
