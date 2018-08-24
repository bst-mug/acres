"""Resource factory

This module provides methods for lazily loading resources.

"""
import logging
import os.path
import pickle
from typing import Dict, Set, List, Tuple

from acres.nn import base, train
from acres.preprocess import create_dumps
from acres.util import functions

logger = logging.getLogger(__name__)

PICKLE_FOLDER = "models/pickle/"
NGRAMS_FOLDER = "models/ngrams/"
LOG_FOLDER = "models/log/"
NN_MODELS_FOLDER = "models/nn/"
DATA_FOLDER = functions.import_conf("CORPUS_PATH")

VERSION = "V6"

#  minimal number of occurrences of a word ngram in the corpus
MIN_FREQ = 2

MORPHEMES = set()  # type: Set[str]
INDEX = {}  # type: Dict[str, Set[int]]
NN_MODEL = None  # type: Word2Vec
NGRAMSTAT = {}  # type: Dict[int, Tuple[int,str]]
CHARACTER_NGRAMS = {}  # type: Dict[str, int]
WORD_NGRAMS = {}  # type: Dict[str, int]


def get_log_corpus_filename() -> str:
    return LOG_FOLDER + "logCorpus.txt"


def get_log_web_filename() -> str:
    return LOG_FOLDER + "logWebs.txt"


def get_morphemes() -> Set[str]:
    global MORPHEMES

    if not MORPHEMES:
        output_file = PICKLE_FOLDER + "morphemes.p"

        if not os.path.isfile(output_file):
            _log_file_not_found(output_file)

            morph_eng = functions.import_conf("MORPH_ENG")
            morph_ger = functions.import_conf("MORPH_GER")

            morphemes = create_dumps.create_morpho_dump(morph_eng)
            morphemes = create_dumps.create_morpho_dump(morph_ger, morphemes)

            pickle.dump(morphemes, open(output_file, "wb"))

        _log_file_found(output_file)
        MORPHEMES = pickle.load(open(output_file, "rb"))

    return MORPHEMES


def get_index() -> Dict[str, Set[int]]:
    global INDEX

    if not INDEX:
        output_file = PICKLE_FOLDER + "index-" + str(MIN_FREQ) + "-" + VERSION + ".p"

        if not os.path.isfile(output_file):
            _log_file_not_found(output_file)

            ngramstat = get_ngramstat()
            index = create_dumps.create_index(ngramstat)
            pickle.dump(index, open(output_file, "wb"))

        _log_file_found(output_file)
        INDEX = pickle.load(open(output_file, "rb"))

    return INDEX


def get_word_ngrams() -> Dict[str, int]:
    """
    Get a not-indexed representation of ngrams.

    :return:
    """
    global WORD_NGRAMS

    if not WORD_NGRAMS:
        pickle_output_file = PICKLE_FOLDER + "wordngrams-" + str(MIN_FREQ) + "-" + VERSION + ".p"
        ngram_output_file = NGRAMS_FOLDER + "ngramstat-" + str(MIN_FREQ) + "-" + VERSION + ".txt"

        if not os.path.isfile(pickle_output_file) or not os.path.isfile(ngram_output_file):
            _log_file_not_found(pickle_output_file)
            _log_file_not_found(ngram_output_file)

            word_ngrams = create_dumps.create_corpus_ngramstat_dump(DATA_FOLDER, MIN_FREQ)

            write_txt(word_ngrams, ngram_output_file)
            pickle.dump(word_ngrams, open(pickle_output_file, "wb"))

        _log_file_found(pickle_output_file)
        WORD_NGRAMS = pickle.load(open(pickle_output_file, "rb"))

    return WORD_NGRAMS


def get_ngramstat() -> Dict[int, Tuple[int,str]]:
    """
    Get an indexed representation of ngrams.

    :return: A dictionary of identifiers mapped to ngrams. Ngrams are tuples with the frequency and
    the corresponding ngram.
    """
    global NGRAMSTAT

    if not NGRAMSTAT:
        output_file = PICKLE_FOLDER + "ngramstat-" + str(MIN_FREQ) + "-" + VERSION + ".p"

        if not os.path.isfile(output_file):
            _log_file_not_found(output_file)

            word_ngrams = get_word_ngrams()
            ngramstat = create_dumps.create_indexed_ngrams(word_ngrams)
            pickle.dump(ngramstat, open(output_file, "wb"))

        _log_file_found(output_file)
        NGRAMSTAT = pickle.load(open(output_file, "rb"))

    return NGRAMSTAT


def get_acronym_ngrams() -> List[str]:
    """
    List of ngrams, containing acronyms

    :return:
    """
    output_file = PICKLE_FOLDER + "acronymNgrams.p"

    if not os.path.isfile(output_file):
        _log_file_not_found(output_file)

        acronym_ngrams = create_dumps.create_new_acro_dump()
        pickle.dump(acronym_ngrams, open(output_file, "wb"))

    _log_file_found(output_file)
    return pickle.load(open(output_file, "rb"))


def get_acronyms() -> List[str]:
    """
    List of acronyms

    :return:
    """
    output_file = PICKLE_FOLDER + "acronyms.p"

    if not os.path.isfile(output_file):
        _log_file_not_found(output_file)

        acronyms = create_dumps.create_acro_dump()
        pickle.dump(acronyms, open(output_file, "wb"))

    _log_file_found(output_file)
    return pickle.load(open(output_file, "rb"))


def get_character_ngrams() -> Dict[str, int]:
    """
    Get character ngrams.

    :return:
    """
    global CHARACTER_NGRAMS

    if not CHARACTER_NGRAMS:
        pickle_output_file = PICKLE_FOLDER + "character_ngrams.p"
        ngram_output_file = NGRAMS_FOLDER + "character_ngrams.txt"

        if not os.path.isfile(pickle_output_file):
            _log_file_not_found(pickle_output_file)
            _log_file_not_found(ngram_output_file)

            character_ngrams = create_dumps.create_corpus_char_stat_dump(DATA_FOLDER)

            write_txt(character_ngrams, ngram_output_file)
            pickle.dump(character_ngrams, open(pickle_output_file, "wb"))

        _log_file_found(pickle_output_file)
        CHARACTER_NGRAMS = pickle.load(open(pickle_output_file, "rb"))

    return CHARACTER_NGRAMS


def get_nn_model(ngram_size=6, min_count=1, net_size=100, alpha=0.025, sg=1, hs=0,
                 negative=5):
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
    global NN_MODEL

    if not NN_MODEL:
        model_path = NN_MODELS_FOLDER + "{}-{}-{}-{}-{}-{}-{}.model".format(ngram_size, min_count,
                                                                            net_size,
                                                                            alpha, sg, hs, negative)

        if not os.path.isfile(model_path):
            logger.warning("Retraining the model...")
            model = train.train(ngram_size, min_count, net_size, alpha, sg, hs, negative)
            model.save(model_path)

        NN_MODEL = base.load_model(model_path)

    return NN_MODEL


def reset():
    """
    Resets global variables to force model recreation.

    :return:
    """
    global MORPHEMES, INDEX, NN_MODEL, NGRAMSTAT, CHARACTER_NGRAMS

    MORPHEMES = set()
    INDEX = {}
    NN_MODEL = None
    NGRAMSTAT = {}
    CHARACTER_NGRAMS = {}


def warmup_cache():
    """
    Warms up the cache of pickle and txt files by calling all the methods.

    :return:
    """
    #get_morphemes()
    get_word_ngrams()
    get_ngramstat()
    get_acronym_ngrams()
    get_acronyms()
    get_index()
    get_character_ngrams()
    get_nn_model()


def write_txt(resource, filename: str) -> int:
    counter = 0

    output = []
    for key in resource:
        output.append("{:10}".format(resource[key]) + "\t" + key)
        counter += 1

    output.sort(reverse=True)

    file = open(filename, 'w', encoding="UTF-8")
    for line in output:
        file.write(line + "\n")
    file.close()

    return counter


def _log_file_not_found(filename: str):
    logger.warning("%s not found, will regenerate.", filename)


def _log_file_found(filename: str):
    logger.info("Loading model from file %s...", filename)


if __name__ == "__main__":
    warmup_cache()
