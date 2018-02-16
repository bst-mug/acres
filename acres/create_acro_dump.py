# Stefan Schulz 12 Nov 2017

import pickle
from acres import Functions

def create_acro_dump():
    """
    Creates and dumps set of acronyms from ngram statistics.

    :return:
    """
    x = pickle.load(open("pickle//acronymNgrams.p", "rb"))
    for i in x:
        print(i)

    1 /0


    a = []
    b = []

    m = pickle.load(open("pickle//ngramstat.p", "rb"))
    for n in m:
        row = (m[n])
        ngram = row.split("\t")[1]
        if ngram.isalnum() and not "Ð" in ngram:
            if Functions.isAcronym(ngram, 7):
                # plausible max length for German medical language
                if not ngram in a: a.append(ngram)

        if " " in ngram:
            tokens = ngram.split(" ")
            for token in tokens:
                if Functions.isAcronym(token, 7):
                    b.append(ngram)
                    break


    # List of acronyms
    pickle.dump(a, open("pickle//acronyms.p", "wb"))
    # List of ngrams, containing acronyms
    pickle.dump(b, open("pickle//acronymNgrams.p", "wb"))


# create_acro_dump()


