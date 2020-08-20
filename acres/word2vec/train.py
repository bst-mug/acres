"""
Trainer for word2vec embeddings based on an idea originally proposed by Johannes Hellrich
(https://github.com/JULIELab/hellrich_dh2016).

.. codeauthor:: Michel Oleynik
"""

import logging

from gensim.models import Word2Vec, Phrases
# from gensim.models import FastText
from gensim.models.phrases import Phraser

from acres.model import ngrams

logger = logging.getLogger(__name__)

WORKERS = 4


def train(ngram_size: int = 6, min_count: int = 1, net_size: int = 100, alpha: float = 0.025,
          sg: int = 1, hs: int = 0, negative: int = 5) -> Word2Vec:
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
    sentences = ngrams.FilteredNGramStat(ngram_size)

    # Find common bigram collocations.
    # Trigrams led to a 2% drop in F1 caused by a 2% drop in recall (though precision increased 2%).
    # TODO debug why "Rechter_Ventrikel" is not generated
    phrases = Phrases(sentences)
    bigram_transformer = Phraser(phrases)
    collocations = bigram_transformer[sentences]

    # model = FastText(size=net_size, window=ngram_size - 1, min_count=min_count)
    # model.build_vocab(sentences=collocations)
    # model.train(sentences=collocations, total_examples=model.corpus_count, epochs=5)

    model = Word2Vec(size=net_size, alpha=alpha, window=ngram_size - 1,
                     min_count=min_count, workers=WORKERS, sg=sg, hs=hs, negative=negative)
    model.build_vocab(sentences=collocations)
    model.train(sentences=collocations, total_examples=model.corpus_count, epochs=5)

    return model

    # Hellrich
    # model = gensim.models.Word2Vec(size=200, window=4, min_count=5, workers=8, alpha=0.01,
    # sg=1, hs=0, negative=5, sample=1e-3)


if __name__ == "__main__":
    MODEL = train(min_count=5)
