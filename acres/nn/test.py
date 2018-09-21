"""Apply a given word2vec model

"""
import logging
from typing import List

from acres.util import acronym as acro_util
from acres.preprocess import resource_factory
from acres.nn import base

logger = logging.getLogger(__name__)


def find_candidates(acronym: str, left_context: str = "", right_context: str = "") -> List[str]:
    """
    Similar to robust_find_embeddings, this finds possible expansions of a given acronym.

    :param acronym:
    :param left_context:
    :param right_context:
    :return:
    """
    model = resource_factory.get_nn_model()

    cleaned_acronym = base.clean(acronym)

    # Check for out of vocabulary acronyms
    # TODO fallback to something, maybe clean the acronym?
    if cleaned_acronym not in model.wv.vocab:
        logger.warning("'%s' not found in the vocabulary!", cleaned_acronym)
        return []

    # TODO evaluate use of context
    # TODO use context somehow
    # [('Kardiomyopathie', 0.772693395614624), ...]
    similar = model.wv.most_similar(positive=cleaned_acronym)

    expansions = []
    for (expansion, _) in similar:
        # TODO experiment with get_acronym_score
        if not acro_util.is_acronym(expansion) and \
                acro_util.is_valid_expansion(cleaned_acronym, expansion):
            expansions.append(expansion)

    return expansions


if __name__ == "__main__":
    print(find_candidates("CMP"))
