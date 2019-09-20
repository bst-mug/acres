import os

from acres.model import topic_list


def test_parse():
    topics = topic_list.parse("tests/resources/test_topics.tsv")
    types = topic_list.unique_types(topics)
    assert 'EKG' in types


def test_create_topic_list(ngramstat):
    filename = "tests/resources/ngram_topics.tsv"
    topic_list.create(filename, 1.0, 3)
    assert os.path.exists(filename)
    assert os.path.getsize(filename) > 10
