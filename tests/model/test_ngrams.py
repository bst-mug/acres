from itertools import islice

from acres.model import ngrams
from acres.util.acronym import Acronym


def test_filter_acronym_contexts():
    sentences = [['Hello', 'my', 'world'], ['performed', 'EKG', 'yesterday']]
    actual = list(islice(ngrams.filter_acronym_contexts(sentences), 100))
    assert actual == [Acronym(acronym='EKG', left_context='performed', right_context='yesterday')]
