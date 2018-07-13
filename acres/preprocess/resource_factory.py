"""Resource factory

This module provides methods for lazily loading resources.

"""

# logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

import os.path
import pickle
from typing import Dict, Set, List, Tuple

from acres import functions
from acres.preprocess import create_dumps

PICKLE_FOLDER = "models/pickle/"
NGRAMS_FOLDER = "models/ngrams/"
LOG_FOLDER = "models/log/"


def get_log_corpus_filename() -> str:
    return LOG_FOLDER + "logCorpus.txt"


def get_log_web_filename() -> str:
    return LOG_FOLDER + "logWebs.txt"


def get_morphemes() -> Set[str]:
    output_file = PICKLE_FOLDER + "morphemes.p"

    if not os.path.isfile(output_file):
        #        _log_file_not_found(output_file)

        morph_eng = functions.import_conf("MORPH_ENG")
        morph_ger = functions.import_conf("MORPH_GER")

        morphemes = create_dumps.create_morpho_dump(morph_eng)
        morphemes = create_dumps.create_morpho_dump(morph_ger, morphemes)

        pickle.dump(morphemes, open(output_file, "wb"))

    return pickle.load(open(output_file, "rb"))


INDEX = {}  # type: Dict[str, Set[int]]


def get_index() -> Dict[str, Set[int]]:
    global INDEX

    if not INDEX:
        output_file = PICKLE_FOLDER + "index" + "-V3.p"

        if not os.path.isfile(output_file):
            _log_file_not_found(output_file)

            ngramstat = get_ngramstat()
            index = create_dumps.create_index(ngramstat)
            pickle.dump(index, open(output_file, "wb"))

        logger.info("Loading index from %s...", output_file)
        INDEX = pickle.load(open(output_file, "rb"))

    return INDEX


def _get_ngramstat_txt() -> str:
    """
    Private auxiliary method to create the ngramstat.txt file. Use get_ngramstat() when possible.

    :return:
    """
    output_file = NGRAMS_FOLDER + "ngramstat" + "V3.txt"

    if not os.path.isfile(output_file):
        #_log_file_not_found(output_file)

        corpus_path = functions.import_conf("CORPUS_PATH")
        ngramstat = create_dumps.create_corpus_ngramstat_dump(corpus_path)
        write_txt(ngramstat, output_file)

    return output_file


NGRAMSTAT = {}  # type: Dict[int, Tuple[int,str]]


def get_ngramstat() -> Dict[int, Tuple[int,str]]:
    """
    Load efficiently the ngramstat file.

    @todo Use tuples instead of strings

    :return: A dictionary of identifiers mapped to ngrams. Ngrams are tab-separated strings
    containing the frequency and the corresponding ngram.
    """
    global NGRAMSTAT

    if not NGRAMSTAT:
        min_freq = 1
        output_file = PICKLE_FOLDER + "ngramstat-" + str(min_freq) + "-V3.p"

        if not os.path.isfile(output_file):
            _log_file_not_found(output_file)

            ngram_file = _get_ngramstat_txt()
            ngramstat = create_dumps.create_ngramstat_dump(ngram_file, min_freq)
            pickle.dump(ngramstat, open(output_file, "wb"))

        logger.info("Loading ngramstat from %s...", output_file)
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

    return pickle.load(open(output_file, "rb"))


def get_tokens() -> Set[str]:
    output_file = PICKLE_FOLDER + "tokens.p"

    if not os.path.isfile(output_file):
        _log_file_not_found(output_file)

        ngram_file = _get_ngramstat_txt()
        ngramstat = create_dumps.create_normalised_token_dump(ngram_file)
        pickle.dump(ngramstat, open(output_file, "wb"))

    return pickle.load(open(output_file, "rb"))


def get_character_ngrams() -> Dict[str, int]:
    pickle_output_file = PICKLE_FOLDER + "character_ngrams.p"
    ngram_output_file = NGRAMS_FOLDER + "character_ngrams.txt"

    if not os.path.isfile(pickle_output_file):
        _log_file_not_found(pickle_output_file)
        _log_file_not_found(ngram_output_file)

        corpus_path = functions.import_conf("CORPUS_PATH")
        character_ngrams = create_dumps.create_corpus_char_stat_dump(corpus_path)

        write_txt(character_ngrams, ngram_output_file)
        pickle.dump(character_ngrams, open(pickle_output_file, "wb"))

    return pickle.load(open(pickle_output_file, "rb"))


def warmup_cache():
    """
    Warms up the cache of pickle and txt files by calling all the methods.

    :return:
    """
    #get_morphemes()
    _get_ngramstat_txt()
    get_ngramstat()
    get_acronym_ngrams()
    get_acronyms()
    get_tokens()
    get_index()
    get_character_ngrams()


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


# def _log_file_not_found(filename: str):
#    logger.warning("%s not found, will regenerate.", filename)


if __name__ == "__main__":
    warmup_cache()
