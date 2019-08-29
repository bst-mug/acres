from acres.model import topic_list


def test_parse():
    topics = topic_list.parse("tests/resources/test_topics.tsv")
    types = topic_list.unique_types(topics)
    assert 'EKG' in types
