"""Base code for word2vec embeddings.

"""

from gensim.models import Word2Vec


def load_model(model_path: str) -> Word2Vec:
    return Word2Vec.load(model_path)
