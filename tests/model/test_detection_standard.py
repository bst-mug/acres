import os

from acres.model import detection_standard
from acres.model.topic_list import Acronym


def test_parse():
    standard = detection_standard.parse("tests/resources/test_detection.tsv")
    assert standard['EKG']
    assert not standard['III']


def test_filter_valid():
    standard = detection_standard.parse("tests/resources/test_detection.tsv")
    filtered = detection_standard.filter_valid(standard)
    assert 'EKG' in filtered
    assert 'III' not in filtered
    assert 'NOTACRONYM' not in filtered


def test_update():
    acronym = Acronym(acronym='AP', left_context='', right_context='')
    actual = detection_standard.update({'EKG': False}, [acronym])
    assert actual == {'EKG': False, 'AP': True}


def test_write():
    filename = "tests/resources/test_detection_write.tsv"
    detection_standard.write(filename, {'EKG': True})
    assert os.path.exists(filename)
    assert os.path.getsize(filename) > 5
