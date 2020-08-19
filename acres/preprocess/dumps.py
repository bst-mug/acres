"""
Module to process the corpus training data and create data structures for speed-up retrieval.

.. codeauthor:: Stefan Schulz
"""
import logging
from typing import Dict, Tuple

from acres import constants
from acres.util import functions
from acres.util import text

logger = logging.getLogger(__name__)


def create_corpus_ngramstat_dump(corpus_path: str, min_freq: int, min_length: int = 1,
                                 max_length: int = 7) -> Dict[str, int]:
    """
    Takes a corpus consisting of text files in a single directory
    Substitutes digits and line breaks
    It requires that all documents are in UTF-8 text.
    It can perform substitutions of digits.

    :param corpus_path:
    :param min_freq:
    :param min_length:
    :param max_length:
    :return:
    """

    docs = []
    counter = 1

    texts = functions.robust_text_import_from_dir(corpus_path)
    length = len(texts)

    logger.info("Creating ngramstat from %d documents...", length)

    break_marker = constants.LINE_BREAK

    for doc in texts:
        if counter % 1000 == 0:
            logger.debug("%d/%d", counter, length)

        # TODO normalize case if not acronym?
        # TODO normalize german characters: ä => ae
        # TODO normalize c = k (soundex?)
        # TODO normalize compositions
        # ("Belastungs-Dyspnoe" = "Belastungs Dyspnoe" = "Belastungsdyspnoe")

        # doc = text.tokenize(doc)
        doc = text.clean(doc)

        doc = text.clear_digits(doc, constants.DIGIT_MARKER)

        doc = doc.replace(break_marker, " " + break_marker + " ")
        doc = text.reduce_repeated_chars(doc, " ", 1)
        doc = doc.replace(break_marker + " " + break_marker, break_marker + break_marker)
        doc = doc.replace(break_marker + " " + break_marker, break_marker + break_marker)
        doc = text.reduce_repeated_chars(doc, break_marker, 2)

        docs.append(doc)
        counter += 1

    entire_corpus = "\n\n".join(docs)

    logger.debug("Corpus length (chars): %d", len(entire_corpus))
    if logger.getEffectiveLevel() == logging.DEBUG:
        import hashlib
        logger.debug("MD5(corpus) = %s", hashlib.md5(entire_corpus.encode("utf-8")).hexdigest())

    dict_ngramstat = functions.create_ngram_statistics(entire_corpus, min_length, max_length)
    logger.debug("ngramstat length (initial): %d", len(dict_ngramstat))

    dict_ngramstat = _filter_frequency(dict_ngramstat, min_freq)
    logger.debug("ngramstat length filtered for frequency: %d", len(dict_ngramstat))

    return dict_ngramstat


def _filter_frequency(ngrams: Dict[str, int], min_freq: int) -> Dict[str, int]:
    """
    Filter a ngram list for ngrams with a minimum frequency.

    :param ngrams:
    :param min_freq:
    :return:
    """
    output = {}
    for (ngram, freq) in ngrams.items():
        if freq >= min_freq:
            output[ngram] = freq
    return output


def create_indexed_ngrams(ngrams: Dict[str, int]) -> Dict[int, Tuple[int, str]]:
    """
    Create an indexed version of a ngram list. This basically adds an unique identifier to every
    (str, int) tuple.

    :param ngrams:
    :return:
    """
    identifier = 1
    output = {}
    for (ngram, freq) in ngrams.items():
        output[identifier] = (freq, ngram)
        identifier += 1
    return output
