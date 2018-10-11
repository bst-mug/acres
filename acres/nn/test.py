"""Apply a given word2vec model

"""
import logging
from typing import List

from acres.preprocess import resource_factory
from acres.nn import base
from acres.rater import rater

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
        # When using Phrases, common collocations (e.g. "koronaren_Herzerkrankung") are shown with
        # '_' as a delimiter
        unglued_expansion = expansion.replace("_", " ")
        if rater.get_acronym_score(cleaned_acronym, unglued_expansion) > 0:
            expansions.append(unglued_expansion)

    return expansions


if __name__ == "__main__":
    print(find_candidates("CMP"))
