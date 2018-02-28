# Stefan Schulz 12 Nov 2017

import collections
import logging
import pickle

from acres import functions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# logger.setLevel(logging.DEBUG) # Uncomment this to get debug messages


def create_normalised_token_dump():
    """
    Creates a set of all tokens in the ngram table, taking into account all possible variants
    typical for clinical German.

    XXX Check whether it's used !!
    INCOMLETE RULESET FOR TRANSFORMING 8 bit to 7 bit
    including normalizing K-C-Z (only relevant for Medical German)
    XXX Soundex ?
    XXX similar function elsewhere?

    :return:
    """
    ngram_stat = functions.import_conf("NGRAMFILE")
    # "..\\..\\stat\corpus_cardio_training_cleaned_1_to_7gram_stat.txt"
    # ngram statistics representing a specific document genre and domain
    logger.debug(ngram_stat)

    all_tokens = set()
    all_token_variants = set()
    with open(ngram_stat) as file:
        for row in file:
            row = row.replace("-", " ").replace("/", " ").replace("(", " ").replace(")", " ")
            tokens = row.split(" ")
            for token in tokens:
                all_tokens.add(token)
        for token in all_tokens:
            token = token.replace(".", "").replace(",", "").replace(";", "")
            token = token.replace(":", "").replace("!", "").replace("?", "")

            all_token_variants.add(token)
            all_token_variants.add(token.lower())
            token = token.replace("k", "c").replace("z", "c")
            all_token_variants.add(token)
            all_token_variants.add(token.lower())
            token = token.replace("ä", "ae").replace(
                "ö", "oe").replace("ü", "ue").replace("ß", "ss")
            all_token_variants.add(token)
            all_token_variants.add(token.lower())
    pickle.dump(all_token_variants, open("tokens.p", "wb"))


def create_ngramstat_dump(ngram_stat_filename, ngramstat, min_freq):
    """
    Creates dump of ngram and ngram variants.
    Create dump of word indices for increasing performance.

    :param ngram_stat_filename:
    :param ngramstat:
    :param min_freq:
    :return:
    """
    with open(ngram_stat_filename) as file:
        identifier = 1
        for row in file:
            if row[8] == "\t":
                # freq = row.split("\t")[0]
                freq = '{:0>7}'.format(int(row.split("\t")[0]))
                ngram = row.split("\t")[1].strip()
                if int(freq) >= min_freq:
                    ngramstat[identifier] = freq + "\t" + ngram
                    identifier += 1
                    # adding variations according to specific tokenization
                    # rules dependent on punctuation chars,
                    # guided by obseverations of German clinical language.
                    if "-" in row:
                        # !!! GERMAN-DEPENDENT !!!
                        # Variant 1: hyphen may be omitted (non-standard German)
                        # "Belastungs-Dyspnoe" -->  "Belastungs Dyspnoe"
                        ngramstat[identifier] = freq + "\t" + ngram.replace("-", " ")
                        identifier += 1
                        # Variant 2: words may be fused (should also be decapitalised
                        # but this is not relevant due to case-insensitive matching)
                        # "Belastungs-Dyspnoe" -->  "BelastungsDyspnoe"
                        ngramstat[identifier] = freq + "\t" + ngram.replace("-", "")
                        identifier += 1
                    if row[-1] in ".:;,-?!/":
                        # Variant 3: removal of trailing punctuation
                        # End of sentence should not restrain reuse of tokens
                        # E.g. "Colonoskopie."
                        # TO DO: investigate solutions to solve it before creating ngrams
                        # !!! FIX ME: sum up frequencies
                        ngramstat[identifier] = freq + "\t" + ngram[:-1]
                        identifier += 1
                    if "/" in row:
                        # Variant 4: insertion of spaces around "/", because
                        # "/" is often used as a token separator with shallow meaning
                        # "/"
                        ngramstat[identifier] = freq + "\t" + ngram.replace("/", " / ")
                        identifier += 1
                    if ", " in row:
                        # Variant 5: insertion of space before comma, to make the
                        # preceding token accessible
                        ngramstat[identifier] = freq + "\t" + \
                                        ngram.replace(", ", " , ")
                        identifier += 1
                    if "; " in row:
                        # the same with semicolon
                        ngramstat[identifier] = freq + "\t" + \
                                        ngram.replace("; ", " ; ")
                        identifier += 1
                    if ": " in row:
                        # the same with colon
                        ngramstat[identifier] = freq + "\t" + \
                                        ngram.replace(": ", " : ")
                        identifier += 1

    index = collections.defaultdict(set)
    for identifier in ngramstat:
        # inverted index for performance issue when retrieving ngram records
        # XXX Think about trie data structure
        # logger.debug(ngramstat[ID])
        ngram = ngramstat[identifier].split("\t")[1]
        words = ngram.split(" ")
        for word in words:
            index[word].add(identifier)
            if len(word) > 1 and not word[-1].isalpha():
                index[word[0:-1]].add(identifier)

    pickle.dump(ngramstat, open("models/pickle/ngramstat.p", "wb"))
    pickle.dump(index, open("models/pickle/index.p", "wb"))


def create_acro_dump():
    """
    Creates and dumps set of acronyms from ngram statistics.

    :return:
    """
    acronym_ngrams = pickle.load(open("models/pickle/acronymNgrams.p", "rb"))
    for i in acronym_ngrams:
        logger.debug(i)

    acronyms = []
    new_acronym_ngrams = []

    ngram_stat = pickle.load(open("models/pickle/ngramstat.p", "rb"))
    for n in ngram_stat:
        row = (ngram_stat[n])
        ngram = row.split("\t")[1]
        if ngram.isalnum() and "Ð" not in ngram:
            if functions.is_acronym(ngram, 7):
                # plausible max length for German medical language
                if ngram not in acronyms:
                    acronyms.append(ngram)

        if " " in ngram:
            tokens = ngram.split(" ")
            for token in tokens:
                if functions.is_acronym(token, 7):
                    new_acronym_ngrams.append(ngram)
                    break

    # List of acronyms
    pickle.dump(acronyms, open("models/pickle/acronyms.p", "wb"))
    # List of ngrams, containing acronyms
    pickle.dump(new_acronym_ngrams, open("models/pickle/acronymNgrams.p", "wb"))


def create_morpho_dump():
    """
    Creates and dumps set of plausible English and German morphemes from morphosaurus dictionary.
    created rather quick & dirty, only for scoring acronym resolutions

    :return:
    """
    morph_eng = functions.import_conf("MORPH_ENG")
    morph_ger = functions.import_conf("MORPH_GER")
    s_morph = set()

    with open(morph_ger) as f:
        for row in f:
            if "<str>" in row:
                row = row.strip()[5:-6]
                row = row.replace("z", "c").replace("k", "c")
                # logger.debug(row)
                s_morph.add(row)

    with open(morph_eng) as f:
        for row in f:
            if "<str>" in row:
                row = row.strip()[5:-6]
                row = row.replace("z", "c").replace("k", "c")
                # logger.debug(row)
                s_morph.add(row)

    pickle.dump(s_morph, open("models/pickle/morphemes.p", "wb"))


def create_corpus_char_stat_dump(corpus_path, ngramlength=8, digit_placeholder="Ð", break_marker="¶"):
    """

    Creates a character ngram statistics from a set of text files
    FIXME: if running this with the whole set of training data it produces an error always
    'charmap' codec can't decode byte 0x81 in position 3417: character maps to <undefined>
    This always happens with the same file
    We have to check this with the local files.
    So far, use the existing token ngram model

    """
    counter = 0
    texts = functions.robust_text_import_from_dir(corpus_path)
    dict_char_ngrams = {}
    f = open("models/ngrams/character_ngrams.txt", 'w', encoding="UTF-8")
    for text in texts:
        print(text)
        str_doc = ""
        counter += 1
        for line in text:
            line = functions.clear_digits(line, digit_placeholder)
            str_doc = str_doc + line.strip() + break_marker
        for i in range(0, len(line) - (ngramlength - 1)):
            ngram = line[0 + i: ngramlength + i].strip()
            if len(ngram) == ngramlength:
                if ngram not in dict_char_ngrams:
                    dict_char_ngrams[ngram] = 1
                else:
                    dict_char_ngrams[ngram] += 1

    # write the ngrams into text file
    out = []
    for n in dict_char_ngrams:
        out.append("{:10}".format(dict_char_ngrams[n]) + "\t" + n)

    out.sort(reverse=True)
    for line in out:
        f.write(line + "\n")
    f.close()
    pickle.dump(dict_char_ngrams, open(
        "models/pickle/character_ngrams.p", "wb", encoding="UTF-8"))


# create_corpus_char_stat_dump("SAMPLEPATH")

# 1 / 0

def create_corpus_ngramstat_dump(corpus_path, fix_lines=True, digit_placeholder="Ð", break_marker="¶"):
    """
    Takes the path with the corpus.
    It requires that all documents are in UTF-8 text.
    It can perform line break cleansing (removes artificial line breaks)
    and substitutions of digits.
    For fixing the lines, a character ngram stat dictionary, CREATED FROM THE SAME OR A SIMILAR
    CORPUS, character_ngrams.p  must be in place.

    :return:
    """
    entire_corpus = ""
    counter = 0
    texts = functions.robust_text_import_from_dir(corpus_path)
    for text in texts:
        if fix_lines:
            dict_char_ngrams = pickle.load(open("pickle//character_ngrams.p", "rb"))
            text = functions.fix_line_endings(text, dict_char_ngrams, "break_marker")
        if len(digit_placeholder) == 1:
            text = functions.clear_digits(
                text, digit_placeholder)
        text = text.replace("  ", " ").replace("  ", " ")
        text = text.replace(
            break_marker, " " + break_marker + " ")
        entire_corpus = entire_corpus + text + "\n\n"
        counter += 1

    logger.debug("Corpus loaded containing %d documents.", counter)
    # = pickle.load(open("models/pickle/character_ngrams.p", "rb"))


# create_corpus_ngramstat_dump()


def load_dumps():
    """
    Load dumps.

    :return:
    """
    logger.info("Begin Read Dump")
    ngramstat = pickle.load(open("pickle//ngramstat.p", "rb"))
    logger.info("-")
    index = pickle.load(open("pickle//index.p", "rb"))
    logger.info("-")
    normalised_tokens = pickle.load(open("pickle//tokens.p", "rb"))
    logger.info("End Read Dump")
