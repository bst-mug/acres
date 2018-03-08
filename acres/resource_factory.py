import os.path
import pickle

from acres import create_dumps
from acres import functions

PREFIX = ""


def get_morphemes():
    output_file = PREFIX + "models/pickle/morphemes.p"

    if not os.path.isfile(output_file):
        morph_eng = functions.import_conf("MORPH_ENG")
        morph_ger = functions.import_conf("MORPH_GER")
        morphemes = create_dumps.create_morpho_dump(morph_eng, morph_ger)
        pickle.dump(morphemes, open(output_file, "wb"))

    return pickle.load(open(output_file, "rb"))


def get_index():
    return pickle.load(open(PREFIX + "models/pickle/index.p", "rb"))


def get_ngramstat():
    return pickle.load(open(PREFIX + "models/pickle/ngramstat.p", "rb"))


def get_acronym_ngrams():
    return pickle.load(open(PREFIX + "models/pickle/acronymNgrams.p", "rb"))


def get_tokens():
    return pickle.load(open(PREFIX + "models/pickle/tokens.p", "rb"))


def get_character_ngrams():
    output_file = PREFIX + "models/pickle/character_ngrams.p"

    if not os.path.isfile(output_file):
        corpus_path = functions.import_conf("CORPUS_PATH")
        morphemes = create_dumps.create_corpus_char_stat_dump(corpus_path)
        pickle.dump(morphemes, open(output_file, "wb"))

    return pickle.load(open(output_file, "rb"))
