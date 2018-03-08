import os.path
import pickle

from acres import create_dumps
from acres import functions

ROOT_FOLDER = "models/pickle/"


def get_morphemes():
    output_file = ROOT_FOLDER + "morphemes.p"

    if not os.path.isfile(output_file):
        morph_eng = functions.import_conf("MORPH_ENG")
        morph_ger = functions.import_conf("MORPH_GER")
        morphemes = create_dumps.create_morpho_dump(morph_eng, morph_ger)
        pickle.dump(morphemes, open(output_file, "wb"))

    return pickle.load(open(output_file, "rb"))


def get_index():
    output_file = ROOT_FOLDER + "index.p"

    if not os.path.isfile(output_file):
        ngramstat = get_ngramstat()
        index = create_dumps.create_index(ngramstat)
        pickle.dump(index, open(output_file, "wb"))

    return pickle.load(open(output_file, "rb"))


def get_ngramstat():
    output_file = ROOT_FOLDER + "ngramstat.p"

    if not os.path.isfile(output_file):
        ngram_file = functions.import_conf("NGRAMFILE")
        ngramstat = create_dumps.create_ngramstat_dump(ngram_file, 2)
        pickle.dump(ngramstat, open(output_file, "wb"))

    return pickle.load(open(output_file, "rb"))


def get_acronym_ngrams():
    """
    List of ngrams, containing acronyms

    :return:
    """
    output_file = ROOT_FOLDER + "acronymNgrams.p"

    if not os.path.isfile(output_file):
        acronym_ngrams = create_dumps.create_new_acro_dump()
        pickle.dump(acronym_ngrams, open(output_file, "wb"))

    return pickle.load(open(output_file, "rb"))


def get_acronyms():
    """
    List of acronyms

    :return:
    """
    output_file = ROOT_FOLDER + "acronyms.p"

    if not os.path.isfile(output_file):
        acronyms = create_dumps.create_acro_dump()
        pickle.dump(acronyms, open(output_file, "wb"))

    return pickle.load(open(output_file, "rb"))


def get_tokens():
    output_file = ROOT_FOLDER + "tokens.p"

    if not os.path.isfile(output_file):
        ngram_file = functions.import_conf("NGRAMFILE")
        ngramstat = create_dumps.create_normalised_token_dump(ngram_file)
        pickle.dump(ngramstat, open(output_file, "wb"))

    return pickle.load(open(output_file, "rb"))


def get_character_ngrams():
    output_file = ROOT_FOLDER + "character_ngrams.p"

    if not os.path.isfile(output_file):
        corpus_path = functions.import_conf("CORPUS_PATH")
        character_ngrams = create_dumps.create_corpus_char_stat_dump(corpus_path)
        pickle.dump(character_ngrams, open(output_file, "wb"))

    return pickle.load(open(output_file, "rb"))
