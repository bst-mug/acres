import os.path

from acres import find_synonym_for_acronyms_in_ngrams


def test_find_synonyms():
    output_file = "tests/models/log/logWebs.txt"

    if os.path.isfile(output_file):
        os.remove(output_file)
    assert not os.path.isfile(output_file)

    find_synonym_for_acronyms_in_ngrams.find_synonyms()
    assert os.path.isfile(output_file)
