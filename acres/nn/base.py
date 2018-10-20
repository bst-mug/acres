"""Base code for word2vec embeddings.

"""
from gensim.models import Word2Vec


def load_model(model_path: str) -> Word2Vec:
    """
    Loads a given model specified by a given filename.

    :param model_path:
    :return:
    """
    return Word2Vec.load(model_path)
