# Stefan Schulz 12 Nov 2017

import collections
import pickle
import os
import logging
from acres import functions


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG) # Uncomment this to get debug messages


def create_normalised_token_dump():
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
    # "..\\..\\stat\corpus_cardio_training_cleaned_1_to_7gram_stat.txt"
    # ngram statistics representing a specific document genre and domain
    print(NGRAMSTAT)

    allTokens = set()
    allTokenVariants = set()
    with open(NGRAMSTAT) as f:
        for row in f:
            row = row.replace("-", " ").replace("/",
                                                " ").replace("(", " ").replace(")", " ")
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
            token = token.replace("ä", "ae").replace(
                "ö", "oe").replace("ü", "ue").replace("ß", "ss")
            allTokenVariants.add(token)
            allTokenVariants.add(token.lower())
    pickle.dump(allTokenVariants, open("tokens.p", "wb"))


def create_ngramstat_dump(ngram_stat_filename, ngramstat, minFreq):
    """
    Creates dump of ngram and ngram variants.
    Create dump of word indices for increasing performance.

    :param ngram_stat_filename:
    :param ngramstat:
    :param minFreq:
    :return:
    """
    with open(ngram_stat_filename) as f:
        ID = 1
        for row in f:
            if row[8] == "\t":
                # freq = '{:0>7}'.format(int(row.split("\t")[0]))
                freq = row.split("\t")[0]
                freq = '{:0>7}'.format(int(row.split("\t")[0]))
                ngram = row.split("\t")[1].strip()
                if int(freq) >= minFreq:
                    ngramstat[ID] = freq + "\t" + ngram
                    ID += 1
                    # adding variations according to specific tokenization
                    # rules dependent on punctuation chars,
                    # guided by obseverations of German clinical language.
                    if "-" in row:
                        # !!! GERMAN-DEPENDENT !!!
                        # Variant 1: hyphen may be omitted (non-standard German)
                        # "Belastungs-Dyspnoe" -->  "Belastungs Dyspnoe"
                        ngramstat[ID] = freq + "\t" + ngram.replace("-", " ")
                        ID += 1
                        # Variant 2: words may be fused (should also be decapitalised
                        # but this is not relevant due to case-insensitive matching)
                        # "Belastungs-Dyspnoe" -->  "BelastungsDyspnoe"
                        ngramstat[ID] = freq + "\t" + ngram.replace("-", "")
                        ID += 1
                    if row[-1] in ".:;,-?!/":
                        # Variant 3: removal of trailing punctuation
                        # End of sentence should not restrain reuse of tokens
                        # E.g. "Colonoskopie."
                        # TO DO: investigate solutions to solve it before creating ngrams
                        # !!! FIX ME: sum up frequencies
                        ngramstat[ID] = freq + "\t" + ngram[:-1]
                        ID += 1
                    if "/" in row:
                        # Variant 4: insertion of spaces around "/", because
                        # "/" is often used as a token separator with shallow meaning
                        # "/"
                        ngramstat[ID] = freq + "\t" + ngram.replace("/", " / ")
                        ID += 1
                    if ", " in row:
                        # Variant 5: insertion of space before comma, to make the
                        # preceding token accessible
                        ngramstat[ID] = freq + "\t" + \
                            ngram.replace(", ", " , ")
                        ID += 1
                    if "; " in row:
                        # the same with semicolon
                        ngramstat[ID] = freq + "\t" + \
                            ngram.replace("; ", " ; ")
                        ID += 1
                    if ": " in row:
                        # the same with colon
                        ngramstat[ID] = freq + "\t" + \
                            ngram.replace(": ", " : ")
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
            if functions.is_acronym(ngram, 7):
                # plausible max length for German medical language
                if not ngram in a:
                    a.append(ngram)

        if " " in ngram:
            tokens = ngram.split(" ")
            for token in tokens:
                if functions.is_acronym(token, 7):
                    b.append(ngram)
                    break

    # List of acronyms
    pickle.dump(a, open("pickle//acronyms.p", "wb"))
    # List of ngrams, containing acronyms
    pickle.dump(b, open("pickle//acronymNgrams.p", "wb"))


def create_morpho_dump():
    """
    Creates and dumps set of plausible English and German morphemes from morphosaurus dictionary.
    created rather quick & dirty, only for scoring acronym resolutions

    :return:
    """
    MORPH_ENG = functions.import_conf("MORPH_ENG")
    MORPH_GER = functions.import_conf("MORPH_GER")
    sMorph = set()

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


def create_corpus_char_stat_dump(corpus_path, ngramlength=8, digit_placeholder="Ð", break_marker="¶"):
    counter = 0
    dict_char_ngrams = {}
    files = os.listdir(corpus_path)
    for file in files:
        str_doc = ""
        with open(corpus_path + "\\" + file, 'r', encoding="UTF-8") as single_document:
            try:
                counter += 1
                for line in single_document:
                    line = functions.clear_digits(line, digit_placeholder)
                    str_doc = str_doc + line.strip() + break_marker
                for i in range(0, len(line) - (ngramlength - 1)):
                    ngram = line[0 + i: ngramlength + i].strip()
                    if len(ngram) == ngramlength:
                        if not ngram in dict_char_ngrams:
                            dict_char_ngrams[ngram] = 1
                        else:
                            dict_char_ngrams[ngram] += 1

            except Exception:
                pass
            single_document.close()

    pickle.dump(dict_char_ngrams, open(
        "models/pickle/character_ngrams.p", "wb"))


# create_corpus_char_stat_dump("data/samples")


def create_corpus_ngramstat_dump(Fixlines=True, digit_placeholder="Ð", break_marker="¶"):
    """
    Takes the path with the corpus.
    It requires that all documents are in UTF-8 text
    It can perform line break cleansing (removes artificial line breaks)
    and substitutions of digits


    :return:
    """
    entire_corpus = ""
    counter = 0
    corpus_path = functions.import_conf("CORPUSPATH")
    files = os.listdir(corpus_path)
    for file in files:
        with open(corpus_path + "\\" + file, 'r', encoding="UTF-8") as single_document:
            document_content = single_document.read()
            # FIXME Undefined variable 'd' (undefined-variable)
            # if Fixlines:
            #     document_content = functions.fix_line_endings(document_content, d, "break_marker")
            if len(digit_placeholder) == 1:
                document_content = functions.clear_digits(
                    document_content, digit_placeholder)
            document_content = document_content.replace(
                "  ", " ").replace("  ", " ")
            document_content = document_content.replace(
                break_marker, " " + break_marker + " ")
        entire_corpus = entire_corpus + document_content + "\n\n"
        counter += 1

    logger.debug("Corpus loaded containing " + str(counter) + " documents.")


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
