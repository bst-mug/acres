import pickle

from acres.get_synonyms_from_ngrams import find_embeddings


def test_find_embeddings():
    pass
    # ngrams = pickle.load(open("models/pickle/ngramstat.p", "rb"))
    # index = pickle.load(open("models/pickle/index.p", "rb"))
    #
    # min_window_size = 5
    # freq = 1
    # max_count = 100
    # min_num_tokens = 6
    # max_num_tokens = 10
    #
    # actual = find_embeddings("re", "OL", "", ngrams, index, min_window_size, freq, max_count, min_num_tokens,
    #                          max_num_tokens)
    # expected = []
    #
    # assert expected == actual
