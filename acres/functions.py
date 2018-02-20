# Stefan Schulz, 18 Mar 2017
"""
Module with functions for corpus analysis.

TODO move to proper function
This function compares and acronym with a potential full form and returns a list of segmentations.
"""

import configparser
import logging
import re
from random import randint

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# logger.setLevel(logging.DEBUG) # Uncomment this to get debug messages


def import_conf(key):
    """

    :param key:
    :return:
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    logger.debug(config.sections())
    return config['DEFAULT'][key]


def import_proxy():
    """

    :return:
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["proxy"]


def split_ngram(ngram):
    """
    Splits a token ngram with acronym(s) into all combinations of left - acro - token.

    :param ngram:
    :return:
    """
    out = []
    lst_tokens = ngram.split(" ")
    c = 0
    for t in lst_tokens:
        if is_acronym(t, 7, "Ð"):
            tr = (" ".join(lst_tokens[0:c]),
                  lst_tokens[c], " ".join(lst_tokens[c + 1:]))
            out.append(tr)
        c = c + 1
    return out


def extract_acronym_definition(str_probe, max_length):
    """
    Identifies potential acronym / definition pairs and extract acronym and definition candidates.

    :param str_probe:
    :param max_length:
    :return:
    """
    str_probe = str_probe.strip()
    if len(str_probe) > 1:
        if str_probe[-1] == ")" and str_probe.count("(") == 1:
            left = str_probe.split("(")[0].strip()  # potential definition
            right = str_probe.split("(")[1][0:-1].strip()   # potential acronym
            if is_acronym(left, max_length, "Ð") and not is_acronym(right, max_length, "Ð"):
                return left, right
            if is_acronym(right, max_length, "Ð") and not is_acronym(left, max_length, "Ð"):
                return right, left


def fix_line_endings(
        long_text,
        char_ngram_dict,
        line_break_marker="¶",
        char_ngram_length=8,
        line_break_marker_position=3):
    """
    addresses the problem that many texts come with
           artificial line breaks. These breaks are removed if
           distributional data show that an unbroken continuation of
           the text is more likely than the break
    :param long_text:
    :param char_ngram_dict:
    :param line_break_marker:
    :param char_ngram_length:
    :param line_break_marker_position:
    :return:
    """

    out = ""
    long_text = long_text.strip().replace("\n", line_break_marker)
    i = 0
    while i + char_ngram_length < len(long_text):
        c = long_text[i]
        ngr = long_text[i:i + char_ngram_length]
        if ngr[line_break_marker_position] == line_break_marker:  # line break marker at nth position
            ngr_clean = clear_digits(ngr, "°")
            ngr_clean_space = ngr_clean.replace(line_break_marker, " ")
            if ngr_clean in char_ngram_dict:
                n_breaks = char_ngram_dict[ngr_clean]
            else:
                n_breaks = 0
            if ngr_clean_space in char_ngram_dict:
                n_spaces = char_ngram_dict[ngr_clean_space]
            else:
                n_spaces = 0
            # TODO: implement logging
            logger.debug("----")
            logger.debug(ngr)
            logger.debug("With new line: %s", n_breaks)
            logger.debug("With space: %s", n_spaces)
            if n_spaces > n_breaks:
                """ TODO: line_break_marker as delimiter
                    What happens if the break marker symbol also occurs in the original text
                    probably safe: using the "¶" character for line breaks
                    Check for whole code how delimiters are handled and how this
                    might interfer with text processing
                """
                out = out + ngr.replace(line_break_marker, " ")
                i = i + char_ngram_length
                if i >= len(long_text):
                    break
            else:
                out = out + c
                i = i + 1
                if i == len(long_text):
                    break
        else:
            out = out + c
            i = i + 1
            if i == len(long_text):
                break

    out = out + long_text[0 - char_ngram_length:] + line_break_marker
    return out.replace(line_break_marker, line_break_marker + "\n")


# for all training files
# added " <EOL>" for end of line and substituted digits by "Ð"


def clear_digits(str_in, substitute_char):
    """
       substitutes all digits by a character (or string)

       Example: ClearDigits("Vitamin B12", "°"):

       :param str_in:
       :param substitute_char:

       """
    out = ""
    for c in str_in:
        if c in "0123456789":
            out = out + substitute_char
        else:
            out = out + c
    return out


def create_ngram_statistics(input_string, n_min, n_max):
    """
    Creates a dictionary that counts each nGram in an input string. Delimiters are spaces.

    Example: bigrams and trigrams
    nMin = 2 ,   nMax = 3
    PROBE: # print(WordNgramStat('a ab aa a a a ba ddd', 1, 4))

    :param input_string:
    :param n_min:
    :param n_max:
    :return:
    """
    output = {}
    lines = input_string.splitlines()
    for line in lines:
        line = line.replace('\r', '')
        line = line.replace('\n', '')
        line = line.strip()
        cleaned_line = line.split(" ")
        for n in range(n_min, n_max + 1):
            for i in range(len(cleaned_line) - n + 1):
                g = ' '.join(cleaned_line[i:i + n])
                output.setdefault(g, 0)
                output[g] += 1
    #    Example for formatted output, sorted, reverse order
    #    for w in sorted(output, key=output.get, reverse = True):
    #       print ('{:>8}'.format(output[w]) + '\t' + w)
    return output


def transliterate_to_seven_bit(str_in, language="de"):
    """
    Converts string to 7-bit ASCII, considering language - specific rules,
    such as in German "Ä" -> "AE", in English "Ä" -> "A"
    Considering in-built capitalization rules such as "ß" -> "SS"
    TODO: completing transliteration rules when non-Western languages are used
    consider using unidecode
    :param str_in:
    :param language: the language for which rules are defined (ISO_639-1)
    :return:
    """
    substitutions = {}
    if language == "de":
        substitutions = {
            "À": "A",
            "Á": "A",
            "Â": "A",
            "Ã": "A",
            "Ä": "AE",
            "Å": "AA",
            "Æ": "AE",
            "Ç": "C",
            "È": "E",
            "É": "E",
            "Ê": "E",
            "Ë": "E",
            "Ì": "I",
            "Í": "I",
            "Î": "I",
            "Ï": "I",
            "Ñ": "N",
            "Ò": "O",
            "Ó": "O",
            "Ô": "O",
            "Õ": "O",
            "Ö": "OE",
            "Ø": "OE",
            "Ù": "U",
            "Ú": "U",
            "Û": "U",
            "Ü": "UE"}
    if language == "en":
        substitutions = {
            "À": "A",
            "Á": "A",
            "Â": "A",
            "Ã": "A",
            "Ä": "A",
            "Å": "A",
            "Æ": "AE",
            "Ç": "C",
            "È": "E",
            "É": "E",
            "Ê": "E",
            "Ë": "E",
            "Ì": "I",
            "Í": "I",
            "Î": "I",
            "Ï": "I",
            "Ñ": "N",
            "Ò": "O",
            "Ó": "O",
            "Ô": "O",
            "Õ": "O",
            "Ö": "O",
            "Ø": "O",
            "Ù": "U",
            "Ú": "U",
            "Û": "U",
            "Ü": "U"}
    return "".join([substitutions.get(c, c) for c in str_in.upper()])


def substitute_k_and_f_by_context(str_in, language="de"):
    """
    Applies normalization rules that improves retrieval of
    clinical terms
    :param str_in:
    :param language: the language for which rules are defined (ISO_639-1)
    :return:
    """
    # no Acronym
    if language == "de":
        if len(str_in) == 1:
            return str_in.isupper()
        if len(str_in) == 2 and str_in[1].isupper():
            return str_in
        if str_in[2].isupper():
            return str_in
        str_in = transliterate_to_seven_bit(str_in)
        return str_in.replace("CAE", "ZAE").replace("COE", "ZOE"). \
            replace("CA", "KA").replace("CA", "KA").replace("CO", "KO"). \
            replace("CU", "KU").replace("CE", "ZE").replace("CI", "ZI"). \
            replace("CY", "ZY").replace("F", "PH")


def is_acronym(str_probe, max_length=7, digit_placeholder="Ð"):
    """
    Identifies Acronyms, restricted by absolute length
    "Ð" as default placeholder for digits. (e.g. "Ð")
    XXX look for "authoritative" definitions for acronyms
    :param str_probe:
    :param max_length:
    :param digit_placeholder:
    :return:
    """
    if len(digit_placeholder) > 1:
        print("Digit placeholders must be empty or a single character")
    ret = False
    s = str_probe.replace(digit_placeholder, "0")
    lower = 0
    upper = 0
    if len(s) <= max_length:
        for c in s:
            if c.isupper():
                upper = upper + 1
            if c.islower():
                lower = lower + 1
    if upper > 1 and upper > lower:
        ret = True
    return ret


def simplify_german_string(str_in_german):
    """
    Decapitalises, substitutes umlauts, sharp s and converts k and z to c

    TODO ... explain why

    :param str_in_german:
    :return:
    """
    str_in_german = str_in_german.lower()
    str_in_german = str_in_german.replace(
        "k", "c").replace("z", "c").replace("ß", "ss")
    str_in_german = str_in_german.replace("é", "e").replace("à", "a")
    return str_in_german.replace("ä", "ae").replace(
        "ö", "oe").replace("ü", "ue")


def diacritics():
    """
    TODO ... explain why

    :return: A string of diacritic characters
    """
    return "µÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ"


def random_sub_list(in_list, max_num):
    """
    Generates random sublist.

    :param in_list:
    :param max_num:
    :return:
    """
    lst_out = []
    length = len(in_list)
    if length <= max_num:
        return in_list
    c = 0
    rnumbers = []
    while c < max_num:
        rnumber = (randint(0, length - 1))
        if rnumber not in rnumbers:
            rnumbers.append(rnumber)
            c = len(rnumbers)
    for rnumber in rnumbers:
        lst_out.append(in_list[rnumber])
    return lst_out


def check_acro_vs_expansion(acro, full):
    import re
    dia = diacritics()
    bina = []
    result = []
    fl = ""
    # remove punctuation chars from full
    for c in full:
        if c.isalpha() or c.isnumeric() or c == " ":
            fl = fl + c
        else:
            fl = fl + " "
    fl = fl.strip()
    # list of binary combinations of
    # alternative regex patterns
    # (greedy vs. non-greedy)
    regs = []  # list of alternative regular expressions
    for i in range(0, (2 ** (len(acro) - 1))):
        str_bin = str(bin(i))[2:].zfill(len(acro) - 1)
        bina.append(str_bin.replace("0", "*|").replace("1", "*?|"))
    for expr in bina:
        lst_exp = expr.split("|")
        z = 0
        out = "^("
        for ex in lst_exp:
            out = out + acro[z] + "." + ex + ")("
            z = z + 1
        regs.append(out[0:-3] + "[A-Za-z" + dia + "0-9 ]*$)")
        # List of all regular expressions
        # print(regs)
        # print(fl)

    for reg in regs:
        if re.search(reg, fl, re.IGNORECASE) is not None:
            result.append(re.findall(reg, fl, re.IGNORECASE)[0])
    return result


# Probes
# print(import_conf("NGRAMFILE"))
# print(CheckAcroVsFull("KHK", "koronare Herzkrankheit"))
# print(extractAcroDef("EKG (Elektrokardiogramm)", 7))
# print(extractAcroDef("Elektrokardiogramm", 7))
# print(extractAcroDef("Elektrokardiogramm (EKG)", 7))

def find_acro_expansions(lst_n_gram_stat):
    """
    Identifies acronyms and looks for possible expansions.
    Takes the most frequent one.
    Uses ngrams with the second token being an acronym.

    TODO: check for what it is needed, complete it
    :param lst_n_gram_stat: A list in which ngrams extracted
    from a corpus are counted in decreasing frequency

    :return:
    """
    letter = ""
    dict_count_per_ngram = {}
    lst_acro = []
    lst_non_acro = []
    is_acro = False
    # TODO: check initialization
    for line in lst_n_gram_stat:
        ngram = line.split("\t")[1]
        count = line.split("\t")[0]
        dict_count_per_ngram[ngram] = count
        if " " in ngram:  # has at least 2 tokens
            other_tokens = " ".join(ngram.split(" ")[1:])
            if len(other_tokens) > 2:
                if is_acronym(other_tokens[1], 7):
                    lst_acro.append(ngram)
                else:
                    for word in ngram.split(" "):
                        is_acro = False
                        if len(word) > 1:
                            if word[1].isupper() or not word.isalpha():
                                is_acro = True
                                break
                    if not is_acro:
                        lst_non_acro.append(ngram)

    for tk in lst_acro:
        counter = 0
        end = " ".join(tk.split(" ")[1:])
        regex = "^"
        for letter in end:
            # regex = regex + letter.upper() + ".*\s" # space required
            regex = regex + letter.upper() + ".*"  # no space required

        for t in lst_non_acro:
            end_n = " ".join(t.split(" ")[1:])
            last_n = " ".join(t.split(" ")[-1])
            if t.split(" ")[0] == tk.split(" ")[0] and not t.split(
                    " ")[1].upper() == tk.split(" ")[1].upper():
                if re.search(regex, end_n.upper()):
                    if letter.upper() in last_n.upper():
                        print(
                            tk +
                            dict_count_per_ngram[tk] +
                            "     " +
                            t +
                            dict_count_per_ngram[t])
                        counter += 1
                        if counter > 4:
                            break


# TODO michel 20180215 move to unit tests
# FindExpansionsOfAcronyms("corpus_cardio_ngramstat.txt")
