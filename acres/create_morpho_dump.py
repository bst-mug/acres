# Stefan Schulz 12 Nov 2017

import pickle

from acres.functions import import_conf

sMorph = set()


def create_morpho_dump():
    """
    Creates and dumps set of plausible English and German morphemes from morphosaurus dictionary.
    created rather quick & dirty, only for scoring acronym resolutions

    :return:
    """
    MORPH_ENG = import_conf("MORPH_ENG")
    MORPH_GER = import_conf("MORPH_GER")

    with open(MORPH_GER) as f:
        for row in f:
            if "<str>" in row:
                row = row.strip()[5:-6]
                row = row.replace("z", "c").replace("k", "c")
                # print(row)
                sMorph.add(row)

    with open(MORPH_ENG) as f:
        for row in f:
            if "<str>" in row:
                row = row.strip()[5:-6]
                row = row.replace("z", "c").replace("k", "c")
                # print(row)
                sMorph.add(row)

    pickle.dump(sMorph, open("pickle//morphemes.p", "wb"))

# create_morpho_dump()
