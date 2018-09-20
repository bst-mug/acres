"""Base code for word2vec embeddings.

"""
import re

from typing import List

from gensim.models import Word2Vec


def load_model(model_path: str) -> Word2Vec:
    return Word2Vec.load(model_path)


def clean(sentence: str) -> str:
    """
    Cleans a given sentence.

    :param sentence:
    :return:
    """
    return " ".join(preprocess(sentence.split(" ")))


def preprocess(tokens: List[str]) -> List[str]:
    """
    Pre-process a given list of tokens by removing special characters.

    :param tokens:
    :return:
    """
    ret = []

    regex_disallowed = re.compile("[^a-zA-ZÐ]")

    for token in tokens:
        # TODO normalize case if not acronym?
        # TODO normalize german characters
        # TODO fix ¶ cleaning bug
        cleaned_token = regex_disallowed.sub("", token)
        if len(cleaned_token) > 0:
            ret.append(cleaned_token)

    # XXX NOOP We should do it in a common way (https://github.com/bst-mug/acres/issues/9)
    return ret
    #return tokens
