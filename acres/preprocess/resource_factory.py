"""Resource factory

This module provides methods for lazily loading resources.

"""
import logging
import os.path
import pickle
from collections import OrderedDict
from typing import Dict, Set, List, Tuple, Any

from gensim.models import Word2Vec

from acres.fastngram import fastngram
from acres.nn import train
from acres.preprocess import dumps
from acres.stats import dictionary
from acres.util import functions

# from gensim.models import FastText

logger = logging.getLogger(__name__)

PICKLE_FOLDER = "models/pickle/"
NGRAMS_FOLDER = "models/ngrams/"
LOG_FOLDER = "models/log/"
NN_MODELS_FOLDER = "models/nn/"
DATA_FOLDER = functions.import_conf("CORPUS_PATH")

VERSION = "V8"

#  minimal number of occurrences of a word ngram in the corpus
MIN_FREQ = 2

MORPHEMES = set()  # type: Set[str]
INDEX = {}  # type: Dict[str, Set[int]]
NN_MODEL = None  # type: Word2Vec
NGRAMSTAT = {}  # type: Dict[int, Tuple[int,str]]
CHARACTER_NGRAMS = {}  # type: Dict[str, int]
WORD_NGRAMS = {}  # type: Dict[str, int]
DICTIONARY = {}  # type: Dict[str, List[str]]
FAST_NGRAM = {}  # type: Dict[int, OrderedDict[int, Dict[str, Set[str]]]]


def get_log_corpus_filename() -> str:
    """
    Get the full path to the `logCorpus.txt` file.

    :return:
    """
    return LOG_FOLDER + "logCorpus.txt"


def get_log_web_filename() -> str:
    """
    Get the full path to the `logWebs.txt` file.

    :return:
    """
    return LOG_FOLDER + "logWebs.txt"


def get_morphemes() -> Set[str]:
    """
    Lazy load the set of morphemes.

    Loading order is as follows:
    1. Variable;
    2. Pickle file;
    3. Generation.

    :return:
    """
    global MORPHEMES

    if not MORPHEMES:
        output_file = PICKLE_FOLDER + "morphemes.p"

        if not os.path.isfile(output_file):
            _log_file_not_found(output_file)

            morph_eng = functions.import_conf("MORPH_ENG")
            morph_ger = functions.import_conf("MORPH_GER")

            morphemes = dumps.create_morpho_dump(morph_eng)
            morphemes = dumps.create_morpho_dump(morph_ger, morphemes)

            _dump(morphemes, output_file)

        _log_file_found(output_file)
        MORPHEMES = _load(output_file)

    return MORPHEMES


def get_index() -> Dict[str, Set[int]]:
    """
    Lazy load the inverted index of ngrams.

    Loading order is as follows:
    1. Variable;
    2. Pickle file;
    3. Generation.

    :return:
    """
    global INDEX

    if not INDEX:
        output_file = PICKLE_FOLDER + "index-" + str(MIN_FREQ) + "-" + VERSION + ".p"

        if not os.path.isfile(output_file):
            _log_file_not_found(output_file)

            ngramstat = get_ngramstat()
            index = dumps.create_index(ngramstat)
            _dump(index, output_file)

        _log_file_found(output_file)
        INDEX = _load(output_file)

    return INDEX


def get_word_ngrams() -> Dict[str, int]:
    """
    Lazy load a not-indexed representation of ngrams.

    Loading order is as follows:
    1. Variable;
    2. Pickle file;
    3. Generation.

    :return:
    """
    global WORD_NGRAMS

    if not WORD_NGRAMS:
        pickle_output_file = PICKLE_FOLDER + "wordngrams-" + str(MIN_FREQ) + "-" + VERSION + ".p"
        ngram_output_file = NGRAMS_FOLDER + "ngramstat-" + str(MIN_FREQ) + "-" + VERSION + ".txt"

        if not os.path.isfile(pickle_output_file) or not os.path.isfile(ngram_output_file):
            _log_file_not_found(pickle_output_file)
            _log_file_not_found(ngram_output_file)

            word_ngrams = dumps.create_corpus_ngramstat_dump(DATA_FOLDER, MIN_FREQ)

            write_txt(word_ngrams, ngram_output_file)
            _dump(word_ngrams, pickle_output_file)

        _log_file_found(pickle_output_file)
        WORD_NGRAMS = _load(pickle_output_file)

    return WORD_NGRAMS


def get_ngramstat() -> Dict[int, Tuple[int, str]]:
    """
    Lazy load an indexed representation of ngrams.

    Loading order is as follows:
    1. Variable;
    2. Pickle file;
    3. Generation.

    :return: A dictionary of identifiers mapped to ngrams. Ngrams are tuples with the frequency \
    and the corresponding ngram.
    """
    global NGRAMSTAT

    if not NGRAMSTAT:
        output_file = PICKLE_FOLDER + "ngramstat-" + str(MIN_FREQ) + "-" + VERSION + ".p"

        if not os.path.isfile(output_file):
            _log_file_not_found(output_file)

            word_ngrams = get_word_ngrams()
            ngramstat = dumps.create_indexed_ngrams(word_ngrams)
            _dump(ngramstat, output_file)

        _log_file_found(output_file)
        NGRAMSTAT = _load(output_file)

    return NGRAMSTAT


def get_acronym_ngrams() -> List[str]:
    """
    Lazy load a list of ngrams containing acronyms.

    Loading order is as follows:
    1. Pickle file;
    2. Generation.

    :return:
    """
    output_file = PICKLE_FOLDER + "acronymNgrams.p"

    if not os.path.isfile(output_file):
        _log_file_not_found(output_file)

        acronym_ngrams = dumps.create_new_acro_dump()
        _dump(acronym_ngrams, output_file)

    _log_file_found(output_file)
    return _load(output_file)


def get_acronyms() -> List[str]:
    """
    Lazy load a list of acronyms.

    Loading order is as follows:
    1. Pickle file;
    2. Generation.

    :return:
    """
    output_file = PICKLE_FOLDER + "acronyms.p"

    if not os.path.isfile(output_file):
        _log_file_not_found(output_file)

        acronyms = dumps.create_acro_dump()
        _dump(acronyms, output_file)

    _log_file_found(output_file)
    return _load(output_file)


def get_character_ngrams() -> Dict[str, int]:
    """
    Lazy load character ngrams.

    Loading order is as follows:
    1. Variable;
    2. Pickle file;
    3. Generation.

    :return:
    """
    global CHARACTER_NGRAMS

    if not CHARACTER_NGRAMS:
        pickle_output_file = PICKLE_FOLDER + "character_ngrams.p"
        ngram_output_file = NGRAMS_FOLDER + "character_ngrams.txt"

        if not os.path.isfile(pickle_output_file):
            _log_file_not_found(pickle_output_file)
            _log_file_not_found(ngram_output_file)

            character_ngrams = dumps.create_corpus_char_stat_dump(DATA_FOLDER)

            write_txt(character_ngrams, ngram_output_file)
            _dump(character_ngrams, pickle_output_file)

        _log_file_found(pickle_output_file)
        CHARACTER_NGRAMS = _load(pickle_output_file)

    return CHARACTER_NGRAMS


def get_nn_model(ngram_size: int = 3, min_count: int = 1, net_size: int = 100, alpha: float = 0.025,
                 sg: int = 0, hs: int = 0, negative: int = 5) -> Word2Vec:
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

        # NN_MODEL = FastText.load(model_path)
        NN_MODEL = Word2Vec.load(model_path)

    return NN_MODEL


def get_dictionary() -> Dict[str, List[str]]:
    """
    Lazy load the sense inventory.

    :return:
    """
    global DICTIONARY

    if not DICTIONARY:
        DICTIONARY = dictionary.parse("resources/acro_full_reference.txt")

    return DICTIONARY


def get_fastngram() -> 'Dict[int, OrderedDict[int, fastngram.ContextMap]]':
    """
    Lazy load the fast n-gram model.

    :return:
    """
    global FAST_NGRAM

    if not FAST_NGRAM:
        pickle_output_file = PICKLE_FOLDER + "fastngram-V2.p"

        if not os.path.isfile(pickle_output_file):
            _log_file_not_found(pickle_output_file)

            fastngram_model = fastngram.optimizer(get_word_ngrams())
            _dump(fastngram_model, pickle_output_file)

        _log_file_found(pickle_output_file)
        FAST_NGRAM = _load(pickle_output_file)

    return FAST_NGRAM


def reset() -> None:
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


def warmup_cache() -> None:
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


def write_txt(resource: Dict[str, int], filename: str) -> int:
    """
    Writes a tab-separated represenation of a dictionary into a file specified by filename.

    :param resource:
    :param filename:
    :return:
    """
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


def _dump(data: Any, filename: str) -> None:
    """
    Dumps data into a file.

    :param data:
    :param filename:
    :return:
    """
    with open(filename, "wb") as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)


def _load(filename: str) -> Any:
    """
    Loads data from a dump file.

    :param filename:
    :return:
    """
    with open(filename, "rb") as file:
        return pickle.load(file)


def _log_file_not_found(filename: str) -> None:
    logger.warning("%s not found, will regenerate.", filename)


def _log_file_found(filename: str) -> None:
    logger.info("Loading model from file %s...", filename)


if __name__ == "__main__":
    warmup_cache()
