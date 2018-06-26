"""Apply a given word2vec model

"""
from acres.nn import base
from typing import List


def find_candidates(acronym: str, left_context: str = "", right_context: str = "") -> List[str]:
    """
    Similar to robust_find_embeddings, this finds possible expansions of a given acronym.

    :param acronym:
    :param left_context:
    :param right_context:
    :return:
    """
    model = base.get_nn_model(min_count=5)

    # Check for out of vocabulary acronyms
    # TODO fallback to something, maybe clean the acronym?
    if acronym not in model.wv.vocab:
        return []

    # TODO evaluate use of context
    # TODO use context somehow
    similar = model.wv.most_similar(
        positive=acronym)  # [('Kardiomyopathie', 0.772693395614624), ...]

    expansions = []
    for (expansion, prob) in similar:
        # TODO filter out invalid expansions
        expansions.append(expansion)

    return expansions


if __name__ == "__main__":
    print(find_candidates("CMP"))
