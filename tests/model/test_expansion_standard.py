import os

from acres.model import expansion_standard
from acres.util.acronym import Acronym


def test_write_results(ngramstat):
    filename = "tests/resources/test.results"
    topics = [Acronym(acronym='EKG', left_context='', right_context=''),
              Acronym(acronym='AP', left_context='', right_context='')]
    expansion_standard.write(filename, {"EKG": {}}, {'EKG', 'AP'}, topics)
    assert os.path.exists(filename)
    assert os.path.getsize(filename) > 10
