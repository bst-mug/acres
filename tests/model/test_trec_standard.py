import os

from acres.model import trec_standard


def test_write_results(ngramstat):
    filename = "tests/resources/test.results"
    trec_standard.write_results(filename, {"EKG": set()})
    assert os.path.exists(filename)
    assert os.path.getsize(filename) > 10
