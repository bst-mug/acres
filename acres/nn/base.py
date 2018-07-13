"""Base code for word2vec embeddings.

"""

import logging
from logging.config import fileConfig

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import os.path

from acres.nn import train
from gensim.models import Word2Vec

MODEL = None  # type: Word2Vec

def get_nn_model(ngram_size=6, min_count=1, net_size=100, alpha=0.025, sg=1, hs=0,
                 negative=5) -> Word2Vec:
    """
    Lazy load a word2vec model.

    :param ngram_size:
    :param min_count:
    :param net_size:
    :param alpha:
    :param sg:
    :param hs:
    :param negative:
    :return:
    """
    global MODEL

    if not MODEL:
        model_path = "models/nn/{}-{}-{}-{}-{}-{}-{}.model".format(ngram_size, min_count, net_size,
                                                                   alpha, sg, hs, negative)

        if not os.path.isfile(model_path):
            logger.warning("Retraining the model...")
            model = train.train(ngram_size, min_count, net_size, alpha, sg, hs, negative)
            model.save(model_path)

        MODEL = Word2Vec.load(model_path)

    return MODEL
