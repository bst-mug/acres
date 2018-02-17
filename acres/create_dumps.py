# Stefan Schulz 12 Nov 2017

import collections
import pickle
from acres import functions


def CreateNormalisedTokenDump():
    """
    Creates a set of all tokens in the ngram table, taking into account all possible variants typical for clinical
    German.

    XXX Check whether it's used !!
    INCOMLETE RULESET FOR TRANSFORMING 8 bit to 7 bit
    including normalizing K-C-Z (only relevant for Medical German)
    XXX Soundex ?
    XXX similar function elsewhere?

    :return:
    """
    NGRAMSTAT = functions.import_conf("NGRAMFILE")
    ##"..\\..\\stat\corpus_cardio_training_cleaned_1_to_7gram_stat.txt"
    # ngram statistics representing a specific document genre and domain
    print(NGRAMSTAT)

    allTokens = set()
    allTokenVariants = set()
    with open(NGRAMSTAT) as f:
        for row in f:
            row = row.replace("-", " ").replace("/", " ").replace("(", " ").replace(")", " ")
            tokens = row.split(" ")
            for token in tokens:
                allTokens.add(token)
        for token in allTokens:
            token = token.replace(".", "").replace(",", "").replace(";", "").replace(":", "").replace("!", "").replace(
                "?", "")
            allTokenVariants.add(token)
            allTokenVariants.add(token.lower())
            token = token.replace("k", "c").replace("z", "c")
            allTokenVariants.add(token)
            allTokenVariants.add(token.lower())
            token = token.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
            allTokenVariants.add(token)
            allTokenVariants.add(token.lower())
    pickle.dump(allTokenVariants, open("tokens.p", "wb"))


def CreateNgramstatDump(nGramStatFile, ngramstat, minFreq):
    """
    Creates dump of ngram and ngram variants.
    Create dump of word indices for increasing performance.

    :param nGramStatFile:
    :param ngramstat:
    :param minFreq:
    :return:
    """
    with open(nGramStatFile) as f:
        ID = 1
        for row in f:
            if row[8] == "\t":
                # freq = '{:0>7}'.format(int(row.split("\t")[0]))
                freq = row.split("\t")[0]
                freq = '{:0>7}'.format(int(row.split("\t")[0]))
                ngram = row.split("\t")[1].strip()
                if int(freq) >= minFreq:
                    ngramstat[ID] = freq + "\t" + ngram;
                    ID += 1
                    # adding variations according to specific tokenization
                    # rules dependent on punctuation chars,
                    # guided by obseverations of German clinical language.
                    if "-" in row:
                        ## !!! GERMAN-DEPENDENT !!!
                        # Variant 1: hyphen may be omitted (non-standard German)
                        # "Belastungs-Dyspnoe" -->  "Belastungs Dyspnoe"
                        ngramstat[ID] = freq + "\t" + ngram.replace("-", " ");
                        ID += 1
                        # Variant 2: words may be fused (should also be decapitalised
                        # but this is not relevant due to case-insensitive matching)
                        # "Belastungs-Dyspnoe" -->  "BelastungsDyspnoe"
                        ngramstat[ID] = freq + "\t" + ngram.replace("-", "");
                        ID += 1
                    if row[-1] in ".:;,-?!/":
                        # Variant 3: removal of trailing punctuation
                        # End of sentence should not restrain reuse of tokens
                        # E.g. "Colonoskopie."
                        # TO DO: investigate solutions to solve it before creating ngrams
                        # !!! FIX ME: sum up frequencies
                        ngramstat[ID] = freq + "\t" + ngram[:-1];
                        ID += 1
                    if "/" in row:
                        # Variant 4: insertion of spaces around "/", because
                        # "/" is often used as a token separator with shallow meaning
                        # "/"
                        ngramstat[ID] = freq + "\t" + ngram.replace("/", " / ");
                        ID += 1
                    if ", " in row:
                        # Variant 5: insertion of space before comma, to make the
                        # preceding token accessible
                        ngramstat[ID] = freq + "\t" + ngram.replace(", ", " , ");
                        ID += 1
                    if "; " in row:
                        # the same with semicolon
                        ngramstat[ID] = freq + "\t" + ngram.replace("; ", " ; ");
                        ID += 1
                    if ": " in row:
                        # the same with colon
                        ngramstat[ID] = freq + "\t" + ngram.replace(": ", " : ");
                        ID += 1

    index = collections.defaultdict(set)
    for ID in ngramstat:
        # inverted index for performance issue when retrieving ngram records
        # XXX Think about trie data structure
        # print(ngramstat[ID])
        ngram = ngramstat[ID].split("\t")[1]
        words = ngram.split(" ")
        for word in words:
            index[word].add(ID)
            if len(word) > 1 and not word[-1].isalpha():
                index[word[0:-1]].add(ID)

    pickle.dump(ngramstat, open("pickle//ngramstat.p", "wb"))
    pickle.dump(index, open("pickle//index.p", "wb"))


ngramstat = {}


# Create pickle dump for min freq 3 (improve performance)
# CreateNgramstatDump(NGRAMSTAT, ngramstat, 3)


def load_dumps():
    """
    Load dumps.

    :return:
    """
    print("Begin Read Dump")
    ngramstat = pickle.load(open("pickle//ngramstat.p", "rb"))
    print("-")
    index = pickle.load(open("pickle//index.p", "rb"))
    print("-")
    normalisedTokens = pickle.load(open("pickle//tokens.p", "rb"))
    print("End Read Dump")



def create_acro_dump():
    """
    Creates and dumps set of acronyms from ngram statistics.

    :return:
    """
    x = pickle.load(open("pickle//acronymNgrams.p", "rb"))
    for i in x:
        print(i)

    1 / 0

    a = []
    b = []

    m = pickle.load(open("pickle//ngramstat.p", "rb"))
    for n in m:
        row = (m[n])
        ngram = row.split("\t")[1]
        if ngram.isalnum() and not "Ð" in ngram:
            if functions.isAcronym(ngram, 7):
                # plausible max length for German medical language
                if not ngram in a: a.append(ngram)

        if " " in ngram:
            tokens = ngram.split(" ")
            for token in tokens:
                if functions.isAcronym(token, 7):
                    b.append(ngram)
                    break

    # List of acronyms
    pickle.dump(a, open("pickle//acronyms.p", "wb"))
    # List of ngrams, containing acronyms
    pickle.dump(b, open("pickle//acronymNgrams.p", "wb"))

# create_acro_dump()


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
