import os.path

from acres.evaluation import corpus


def test_find_synonyms():
    output_file = "tests/models/log/logWebs.txt"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    corpus.find_synonyms()
    assert os.path.isfile(output_file)
