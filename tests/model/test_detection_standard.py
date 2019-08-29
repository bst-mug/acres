from acres.model import detection_standard


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
