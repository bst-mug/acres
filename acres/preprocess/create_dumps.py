"""
Stefan Schulz 12 Nov 2017
"""
import collections
import logging
import re
from typing import Dict, Set, List, Tuple, Optional

from acres.preprocess import resource_factory
from acres.util import acronym
from acres.util import functions
from acres.util import text

logger = logging.getLogger(__name__)


def create_corpus_char_stat_dump(corpus_path: str, ngramlength: int = 8,
                                 digit_placeholder: str = "Ð", break_marker: str = "¶") -> Dict[str, int]:
    """
    - Takes a corpus consisting of text files in a single directory
    - Substitutes digits and line breaks
    - Generates a statistics of character ngrams including the digit and break substitutes
    - Purpose: To substitute artificial breaks in a corpus
    - returns counter (number of records)
    """
    texts = functions.robust_text_import_from_dir(corpus_path)

    logger.info("Creating character ngrams from %d documents...", len(texts))

    dict_char_ngrams = {}   # type: Dict[str, int]

    for doc in texts:
        str_doc = ""
        lines = doc.split("\n")
        for line in lines:
            line = text.clear_digits(line, digit_placeholder)
            str_doc = str_doc + line.strip() + break_marker
        for i in range(0, len(str_doc) - (ngramlength - 1)):
            ngram = str_doc[0 + i: ngramlength + i]
            if len(ngram) == ngramlength:
                if ngram not in dict_char_ngrams:
                    dict_char_ngrams[ngram] = 1
                else:
                    dict_char_ngrams[ngram] += 1

    return dict_char_ngrams


def create_corpus_ngramstat_dump(corpus_path: str, min_freq: int, min_length: int = 1,
                                 max_length: int = 7, digit_placeholder: str = "Ð",
                                 break_marker: str = "¶", fix_lines: bool = True) -> Dict[str, int]:
    """
    Takes a corpus consisting of text files in a single directory
    Substitutes digits and line breaks
    It requires that all documents are in UTF-8 text.
    It can perform line break cleansing (removes artificial line breaks)
    and substitutions of digits.
    For fixing the lines, a character ngram stat dictionary,
    CREATED FROM THE SAME OR A SIMILAR
    CORPUS, character_ngrams.p  must be in place.

    :param corpus_path:
    :param min_freq:
    :param min_length:
    :param max_length:
    :param digit_placeholder:
    :param break_marker:
    :param fix_lines:
    :return:
    """

    docs = []
    counter = 1

    texts = functions.robust_text_import_from_dir(corpus_path)
    length = len(texts)

    logger.info("Creating ngramstat from %d documents...", length)

    for doc in texts:
        if counter % 1000 == 0:
            logger.debug("%d/%d", counter, length)

        if fix_lines:
            doc = text.fix_line_endings(doc, break_marker)

        # TODO normalize case if not acronym?
        # TODO normalize german characters: ä => ae
        # TODO normalize c = k (soundex?)
        # TODO normalize compositions
        # ("Belastungs-Dyspnoe" = "Belastungs Dyspnoe" = "Belastungsdyspnoe")

        # doc = text.tokenize(doc)
        doc = text.clean(doc)

        if len(digit_placeholder) == 1:
            doc = text.clear_digits(doc, digit_placeholder)
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


def create_index(ngramstat: Dict[int, Tuple[int, str]]) -> Dict[str, Set[int]]:
    """
    Create an inverted index for performance issue when retrieving ngram records.

    :param ngramstat:
    :return:
    """
    index = collections.defaultdict(set)    # type: Dict[str, Set[int]]
    for identifier in ngramstat:
        # XXX Think about trie data structure
        # logger.debug(ngramstat[ID])
        (_, ngram) = ngramstat[identifier]
        words = ngram.split(" ")
        for word in words:
            index[word].add(identifier)
            if len(word) > 1 and not word[-1].isalpha():
                index[word[0:-1]].add(identifier)

    return index


def create_acro_dump() -> List[str]:
    """
    Creates and dumps set of acronyms from ngram statistics.

    :return:
    """
    # acronym_ngrams = resource_factory.get_acronym_ngrams()
    # for i in acronym_ngrams:
    #   logger.debug(i)
    counter = 0
    acronyms = []   # type: List[str]

    ngram_stat = resource_factory.get_ngramstat()
    for entry in ngram_stat:
        row = (ngram_stat[entry])
        (_, ngram) = row
        if ngram.isalnum() and "Ð" not in ngram:
            if acronym.is_acronym(ngram, 7):
                # plausible max length for German medical language
                if ngram not in acronyms:
                    acronyms.append(ngram)
                    counter += 1

    return acronyms


def create_new_acro_dump() -> List[str]:
    """

    :return:
    """

    counter = 0
    new_acronym_ngrams = []

    ngram_stat = resource_factory.get_ngramstat()
    for n in ngram_stat:
        row = (ngram_stat[n])
        (_, ngram) = row
        if " " in ngram:
            tokens = ngram.split(" ")
            for token in tokens:
                if acronym.is_acronym(token, 7):
                    new_acronym_ngrams.append(ngram)
                    counter += 1
                    break

    return new_acronym_ngrams


def create_morpho_dump(lexicon_file: str, append_to: Optional[Set] = None) -> Set[str]:
    """
    Creates and dumps set of plausible English and German morphemes
    from morphosaurus dictionary.
    TODO: created rather quick & dirty, only for scoring acronym resolutions

    :return:
    """
    append_to = append_to or set()

    with open(lexicon_file) as file:
        for row in file:
            if "<str>" in row:
                row = row.strip()[5:-6]
                row = row.replace("z", "c").replace("k", "c")
                # logger.debug(row)
                append_to.add(row)

    return append_to

