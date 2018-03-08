import pickle

PREFIX = ""


def get_morphemes():
    return pickle.load(open(PREFIX + "models/pickle/morphemes.p", "rb"))


def get_index():
    return pickle.load(open(PREFIX + "models/pickle/index.p", "rb"))


def get_ngramstat():
    return pickle.load(open(PREFIX + "models/pickle/ngramstat.p", "rb"))


def get_acronym_ngrams():
    return pickle.load(open(PREFIX + "models/pickle/acronymNgrams.p", "rb"))


def get_tokens():
    return pickle.load(open(PREFIX + "models/pickle/tokens.p", "rb"))
