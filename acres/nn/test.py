"""Apply a given word2vec model

"""
import logging
from typing import Iterator, Tuple

from gensim.models import Word2Vec

from acres.preprocess import resource_factory

logger = logging.getLogger(__name__)


def find_candidates(acronym: str, left_context: str = "", right_context: str = "",
                    min_distance: float = 0.0, max_rank: int = 500) -> Iterator[str]:
    """
    Similar to robust_find_embeddings, this finds possible expansions of a given acronym.

    :param acronym:
    :param left_context:
    :param right_context:
    :param min_distance:
    :param max_rank:
    :return:
    """
    model = resource_factory.get_nn_model()

    # Check for out of vocabulary acronyms
    # TODO fallback to something, maybe clean the acronym?
    if acronym not in model.wv.vocab:
        logger.warning("'%s' not found in the vocabulary!", acronym)
        return []

    # TODO evaluate use of context
    # [('Kardiomyopathie', 0.772693395614624), ...]
    similar = _most_similar(model, acronym)

    rank = 0
    for (expansion, distance) in similar:
        if distance < min_distance or rank > max_rank:
            return ""
        rank += 1
        # When using Phrases, common collocations (e.g. "koronaren_Herzerkrankung") are shown
        # with '_' as a delimiter.
        yield expansion.replace("_", " ")


def _most_similar(model: Word2Vec, positive: str) -> Iterator[Tuple[str, float]]:
    """
    A generator version of gensim's `most_similar` method.

    :param model:
    :param positive:
    :return:
    """
    ratio = 10
    start = 0
    stop = 100
    while True:
        expansions = model.wv.most_similar(positive=positive, topn=stop)
        for i in range(start, stop):
            if i >= len(expansions):
                return ""
            yield expansions[i]
        start = stop
        stop *= ratio


if __name__ == "__main__":
    print(find_candidates("CMP"))
