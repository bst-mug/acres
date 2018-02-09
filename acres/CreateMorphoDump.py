# Creates and dumps set of plausible English and German morphemes 
# from morphosaurus dictionary
# Stefan Schulz 12 Nov 2017

# created rather quick & dirty, only for scoring acronym resolutions

import pickle

sMorph = set()

MORPH_ENG = "C:\\Users\\schulz\\Nextcloud\\Terminology\\Morpho\\morphosaurus\\params\\english\\lex_en.xml"
MORPH_GER = "C:\\Users\\schulz\\Nextcloud\\Terminology\\Morpho\\morphosaurus\\params\\german\\lex_de.xml"


with open(MORPH_GER) as f:
    for row in f:
        if "<str>" in row:
            row = row.strip()[5:-6]
            row = row.replace("z", "c").replace("k", "c")
            #print(row)
            sMorph.add(row)

with open(MORPH_ENG) as f:
    for row in f:
        if "<str>" in row:
            row = row.strip()[5:-6]
            row = row.replace("z", "c").replace("k", "c")
            #print(row)
            sMorph.add(row)

pickle.dump(sMorph, open("pickle//morphemes.p", "wb"))
 

