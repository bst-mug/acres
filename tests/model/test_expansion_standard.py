import os

from acres.model import expansion_standard


def test_write_results(ngramstat):
    filename = "tests/resources/test.results"
    expansion_standard.write_results(filename, {"EKG": set()})
    assert os.path.exists(filename)
    assert os.path.getsize(filename) > 10
