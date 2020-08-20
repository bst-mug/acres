import os.path

from acres.preprocess import resource_factory
from acres.preprocess import dumps


def test_fixture():
    assert "tests" in resource_factory.PICKLE_FOLDER


def test_get_ngramstat(monkeypatch, ngramstat):
    # Monkey patch create_indexed_ngrams so that it returns the fake ngramstat
    def mockreturn(word_ngrams):
        return ngramstat
    monkeypatch.setattr(dumps, "create_indexed_ngrams", mockreturn)

    resource_factory.MIN_FREQ = 1
    
    output_file = "tests/models/pickle/ngramstat-1-" + resource_factory.VERSION + ".p"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    # Forces recreation
    resource_factory.NGRAMSTAT = []

    resource_factory.get_ngramstat()
    assert os.path.isfile(output_file)
