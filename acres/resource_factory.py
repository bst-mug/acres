import pickle

PREFIX = ""


def get_morphemes():
    return pickle.load(open(PREFIX + "models/pickle/morphemes.p", "rb"))
