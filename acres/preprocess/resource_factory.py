"""
Resource factory. This module provides methods for lazily loading resources.

.. codeauthor:: Michel Oleynik
"""
import logging
import os.path
import pickle
from typing import Dict, List, Tuple, Any

from gensim.models import Word2Vec

from acres.fastngram import fastngram
from acres.word2vec import train
from acres.preprocess import dumps
from acres.stats import dictionary
from acres.util import functions

# from gensim.models import FastText

logger = logging.getLogger(__name__)

PICKLE_FOLDER = "models/pickle/"
NGRAMS_FOLDER = "models/ngrams/"
NN_MODELS_FOLDER = "models/word2vec/"
DATA_FOLDER = functions.import_conf("CORPUS_PATH")

VERSION = "V10"

#  minimal number of occurrences of a word ngram in the corpus
MIN_FREQ = 2

NN_MODEL = None  # type: Word2Vec
NGRAMSTAT = {}  # type: Dict[int, Tuple[int,str]]
WORD_NGRAMS = {}  # type: Dict[str, int]
DICTIONARY = {}  # type: Dict[str, List[str]]
CONTEXT_MAP = {}  # type: Dict[int, fastngram.ContextMap]
CENTER_MAP = {}  # type: Dict[int, fastngram.CenterMap]


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
        model_path = NN_MODELS_FOLDER + "{}-{}-{}-{}-{}-{}-{}-{}.model"\
            .format(ngram_size, min_count, net_size, alpha, sg, hs, negative, VERSION)

        if not os.path.isfile(model_path):
            logger.warning("Retraining the model...")
            model = train.train(ngram_size, min_count, net_size, alpha, sg, hs, negative)
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
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


def get_context_map(partition: int = 0) -> 'fastngram.ContextMap':
    """
    Lazy load the fast n-gram context map model.

    :return:
    """
    global CONTEXT_MAP

    if partition not in CONTEXT_MAP:
        # Reset the context map to reduce memory consumption
        CONTEXT_MAP = {}

        pickle_output_file = "{}fastngram-{}/contextMap-{}.p"\
            .format(PICKLE_FOLDER, VERSION, str(partition))

        if not os.path.isfile(pickle_output_file):
            _log_file_not_found(pickle_output_file)

            context_map = fastngram.create_map(get_word_ngrams(), fastngram.ContextMap(), partition)
            _dump(context_map, pickle_output_file)

        _log_file_found(pickle_output_file)
        CONTEXT_MAP[partition] = _load(pickle_output_file)

    return CONTEXT_MAP[partition]


def get_center_map(partition: int = 0) -> 'fastngram.CenterMap':
    """
    Lazy load the fast n-gram center map model.

    :return:
    """
    global CENTER_MAP

    if partition not in CENTER_MAP:
        # Reset the center map to reduce memory consumption
        CENTER_MAP = {}

        pickle_output_file = "{}fastngram-{}/centerMap-{}.p"\
            .format(PICKLE_FOLDER, VERSION, str(partition))

        if not os.path.isfile(pickle_output_file):
            _log_file_not_found(pickle_output_file)

            center_map = fastngram.create_map(get_word_ngrams(), fastngram.CenterMap(), partition)
            _dump(center_map, pickle_output_file)

        _log_file_found(pickle_output_file)
        CENTER_MAP[partition] = _load(pickle_output_file)

    return CENTER_MAP[partition]


def reset() -> None:
    """
    Resets global variables to force model recreation.

    :return:
    """
    global NN_MODEL, NGRAMSTAT

    NN_MODEL = None
    NGRAMSTAT = {}


def warmup_cache() -> None:
    """
    Warms up the cache of pickle and txt files by calling all the methods.

    :return:
    """
    get_word_ngrams()
    get_ngramstat()
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

    os.makedirs(os.path.dirname(filename), exist_ok=True)
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
    logger.debug("Dumping %s...", filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
    logger.debug("Dumped.")


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
