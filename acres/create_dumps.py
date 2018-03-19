# Stefan Schulz 12 Nov 2017

import collections
import logging

from acres import functions
from acres import resource_factory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# logger.setLevel(logging.DEBUG) # Uncomment this to get debug messages

def create_corpus_char_stat_dump(corpus_path, ngramlength=8, digit_placeholder="Ð", break_marker="¶"):
    """
    - Takes a corpus consisting of text files in a single directory
    - Substitutes digits and line breaks
    - Generates a statistics of character ngrams including the digit and break substitutes
    - Purpose: To substitute artificial breaks in a corpus
    - returns counter (number of records)
    """
    counter = 0
    texts = functions.robust_text_import_from_dir(corpus_path)
    dict_char_ngrams = {}

    for text in texts:
        str_doc = ""
        lines = text.split("\n")
        for line in lines:
            line = functions.clear_digits(line, digit_placeholder)
            str_doc = str_doc + line.strip() + break_marker
        for i in range(0, len(str_doc) - (ngramlength - 1)):
            ngram = str_doc[0 + i: ngramlength + i].strip()
            if len(ngram) == ngramlength:
                if ngram not in dict_char_ngrams:
                    dict_char_ngrams[ngram] = 1
                else:
                    dict_char_ngrams[ngram] += 1

    return dict_char_ngrams


# TODO : we have to assure that unit tests with small input data do not
# TODO : overwrite the models (ngram and pickle)

def create_corpus_ngramstat_dump(corpus_path, fix_lines=True, min_length=1, max_length=7, digit_placeholder="Ð",
                                 break_marker="¶"):
    """
    Takes a corpus consisting of text files in a single directory
    Substitutes digits and line breaks
    It requires that all documents are in UTF-8 text.
    It can perform line break cleansing (removes artificial line breaks)
    and substitutions of digits.
    For fixing the lines, a character ngram stat dictionary, CREATED FROM THE SAME OR A SIMILAR
    CORPUS, character_ngrams.p  must be in place.
    Creates a text file with token n gram statistics
    :return:  counter ( number of records)
    """
    entire_corpus = ""
    counter = 0

    texts = functions.robust_text_import_from_dir(corpus_path)

    for text in texts:
        if fix_lines:
            text = functions.fix_line_endings(text, break_marker)
        if len(digit_placeholder) == 1:
            text = functions.clear_digits(
                text, digit_placeholder)
        text = text.replace("  ", " ").replace("  ", " ")
        text = text.replace(break_marker, " " + break_marker + " ")
        entire_corpus = entire_corpus + text + "\n\n"
        counter += 1

    logger.debug("Corpus loaded containing %d documents.", counter)
    dict_ngramstat = functions.create_ngram_statistics(entire_corpus, min_length, max_length)

    # pickle.dump(dict_ngramstat, open("models/pickle/token_ngrams.p", "wb"))
    return dict_ngramstat


def create_ngramstat_dump(ngram_stat_filename, min_freq=2):
    """
    Creates dump of ngram and ngram variants.
    Create dump of word indices for increasing performance.

    :param ngram_stat_filename:
    :param min_freq:
    :return:
    """
    ngramstat = {}

    with open(ngram_stat_filename, 'r', encoding="UTF-8") as file:
        identifier = 1
        for row in file:
            if row[10] == "\t":
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

    return ngramstat


def create_index(ngramstat):
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

    return index


def create_normalised_token_dump(ngram_stat):
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

    # ngram statistics representing a specific document genre and domain

    logger.debug(ngram_stat)
    all_tokens = set()
    all_token_variants = set()
    with open(ngram_stat, 'r', encoding="UTF-8") as file:
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

    return all_token_variants


def create_acro_dump():
    """
    Creates and dumps set of acronyms from ngram statistics.

    :return:
    """
    # acronym_ngrams = resource_factory.get_acronym_ngrams()
    # for i in acronym_ngrams:
    #   logger.debug(i)
    counter = 0
    acronyms = []

    ngram_stat = resource_factory.get_ngramstat()
    for n in ngram_stat:
        row = (ngram_stat[n])
        ngram = row.split("\t")[1]
        if ngram.isalnum() and "Ð" not in ngram:
            if functions.is_acronym(ngram, 7):
                # plausible max length for German medical language
                if ngram not in acronyms:
                    acronyms.append(ngram)
                    counter += 1

    return acronyms


def create_new_acro_dump():
    """

    :return:
    """

    counter = 0
    new_acronym_ngrams = []

    ngram_stat = resource_factory.get_ngramstat()
    for n in ngram_stat:
        row = (ngram_stat[n])
        ngram = row.split("\t")[1]
        if " " in ngram:
            tokens = ngram.split(" ")
            for token in tokens:
                if functions.is_acronym(token, 7):
                    new_acronym_ngrams.append(ngram)
                    counter += 1
                    break

    return new_acronym_ngrams


def create_morpho_dump(lexicon_file, append_to=set()):
    """
    Creates and dumps set of plausible English and German morphemes
    from morphosaurus dictionary.
    TODO: created rather quick & dirty, only for scoring acronym resolutions

    :return:
    """

    with open(lexicon_file) as f:
        for row in f:
            if "<str>" in row:
                row = row.strip()[5:-6]
                row = row.replace("z", "c").replace("k", "c")
                # logger.debug(row)
                append_to.add(row)

    return append_to
