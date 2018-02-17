# Stefan Schulz, 18 Mar 2017
"""
Module with functions for corpus analysis.

TODO move to proper function
This function compares and acronym with a potential full form and returns a list of segmentations.
"""

import configparser
import re
from random import randint

def import_conf(key):
    """

    :param key:
    :return:
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    print(config.sections())
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
    lTokens = ngram.split(" ")
    c = 0
    for t in lTokens:
        if is_acronym(t, 7, "Ð"):
            tr = (" ".join(lTokens[0:c]), lTokens[c], " ".join(lTokens[c + 1:]))
            out.append(tr)
        c = c + 1
    return out

def extract_acronym_definition(strProbe, maxLength):
    """
    Identifies potential acronym / definition pairs and extract acronym and definition candidates.

    :param strProbe:
    :param maxLength:
    :return:
    """
    strProbe = strProbe.strip()
    if len(strProbe) > 1:
        if strProbe[-1] == ")" and strProbe.count("(") == 1:
            left = strProbe.split("(")[0].strip()
            right = strProbe.split("(")[1][0:-1].strip()
            if is_acronym(left, maxLength, "Ð") and not is_acronym(right, maxLength, "Ð"):
                return (left, right)
            if is_acronym(right, maxLength, "Ð") and not is_acronym(left, maxLength, "Ð"):
                return (right, left)






def fix_line_endings(long_text, char_ngram_dict, line_break_marker = "¶", char_ngram_length = 8,
                     line_break_marker_position = 3 ):
    """
           addresses the problem that many texts come with
           artificial line breaks. These breaks are removed if
           distributional data show that an unbroken continuation of
           the text is more likely than the break

           :param InputString:
           :param nMin:
           :param nMax:
           :return:
           """
    out = ""
    verbose = False
    long_text = long_text.strip().replace("\n", line_break_marker)
    l = len(long_text)
    i = 0
    while i + char_ngram_length < l:
        c = long_text[i]
        ngr = long_text[i:i + char_ngram_length]
        if ngr[line_break_marker_position] == line_break_marker:   # line break marker at nth position
            ngrClean = ClearDigits(ngr, "°")
            ngrCleanSpace = ngrClean.replace(line_break_marker, " ")
            if ngrClean in char_ngram_dict:
                nBreaks = char_ngram_dict[ngrClean]
            else:
                nBreaks = 0
            if ngrCleanSpace in char_ngram_dict:
                nSpaces = char_ngram_dict[ngrCleanSpace]
            else:
                nSpaces = 0
            # TODO: implement logging
            if verbose: print("----")
            if verbose: print(ngr)
            if verbose: print("With new line: ", nBreaks)
            if verbose: print("With space: ", nSpaces)
            if nSpaces > nBreaks:
                # TODO: line_break_marker as delimiter inserted
                # TODO: What happens if the break marker symbol also occurs in the original text
                # TODO: probably safe: using the "¶" character for line breaks
                # TODO: Check for whole code how delimiters are handled and how this
                # TODO: might interfer with text processing
                out = out + ngr.replace(line_break_marker, " ")
                i = i + char_ngram_length
                if i >= l: break
            else:
                out = out + c
                i = i + 1
                if i == l: break
        else:
            out = out + c
            i = i + 1
            if i == l: break

    out = out + long_text[0 - char_ngram_length:] + line_break_marker
    return out.replace(line_break_marker, line_break_marker + "\n")


# for all training files
# added " <EOL>" for end of line and substituted digits by "Ð"




def clear_digits(strIn, substituteChar):
    """
       substitutes all digits by a character (or string)

       Example: ClearDigits("Vitamin B12", "°"):

       :param InputString:
       :param nMin:
       :param nMax:
       :return: "Vitamin B°°"
       """
    out = ""
    for c in strIn:
        if c in "0123456789": out = out + substituteChar
        else: out = out + c
    return out

def create_ngram_statistics(InputString, nMin, nMax):
    """
    Creates a dictionary that counts each nGram in an input string. Delimiters are spaces.

    Example: bigrams and trigrams
    nMin = 2 ,   nMax = 3
    PROBE: # print(WordNgramStat('a ab aa a a a ba ddd', 1, 4))

    :param InputString:
    :param nMin:
    :param nMax:
    :return:
    """
    output = {}
    lines = InputString.splitlines()
    for line in lines:
        line = line.replace('\r', '')
        line = line.replace('\n', '')
        line = line.strip()
        cleaned_line = line.split(" ")
        for n in range(nMin, nMax + 1):
            for i in range(len(cleaned_line) - n + 1):
                g = ' '.join(cleaned_line[i:i + n])
                output.setdefault(g, 0)
                output[g] += 1
    #    Example for formatted output, sorted, reverse order
    #    for w in sorted(output, key=output.get, reverse = True):
    #       print ('{:>8}'.format(output[w]) + '\t' + w)
    return output


def transliterate_to_seven_bit(strIn, language ="DE"):
    """
    Converts string to 7-bit ASCII, considering language - specific rules,
    such as in German "Ä" -> "AE", in English "Ä" -> "A"
    Considering in-built capitalization rules such as "ß" -> "SS"
    TODO: completing transliteration rules when non-Western languages are used
    consider using unidecode
    :param strIn:
    :return:
    """
    if language == "DE":
        substitutions = {"À": "A" , "Á": "A" , "Â": "A" , "Ã": "A" ,
        "Ä": "AE" , "Å": "AA" , "Æ": "AE" , "Ç": "C" , "È": "E" ,
    "É": "E" , "Ê": "E" , "Ë": "E" , "Ì": "I" , "Í": "I" , "Î": "I" ,
    "Ï": "I" , "Ñ": "N" , "Ò": "O" , "Ó": "O" , "Ô": "O" , "Õ": "O" ,
    "Ö": "OE" , "Ø": "OE" , "Ù": "U" , "Ú": "U" , "Û": "U" , "Ü": "UE"}
    if language == "EN":
        substitutions = {"À": "A", "Á": "A", "Â": "A", "Ã": "A",
         "Ä": "A", "Å": "A", "Æ": "AE", "Ç": "C", "È": "E",
         "É": "E", "Ê": "E", "Ë": "E", "Ì": "I", "Í": "I", "Î": "I",
          "Ï": "I", "Ñ": "N", "Ò": "O", "Ó": "O", "Ô": "O", "Õ": "O",
           "Ö": "O", "Ø": "O", "Ù": "U", "Ú": "U", "Û": "U", "Ü": "U"}
    return "".join([substitutions.get(c, c) for c in strIn.upper()])


def substitute_k_and_f_by_context(strIn, language ="DE"):
    """
    Applies normalization rules that improves retrieval of
    clinical terms
    :param strIn:
    :return:
    """
    # no Acronym
    if language == "DE":
        if len(strIn) == 1:
            return strIn.isupper()
        if len(strIn) == 2 and strIn[1].isupper():
            return strIn
        if strIn[2].isupper():
            return strIn
        strIn = transliterate_to_seven_bit(strIn)
        return strIn.replace("CAE", "ZAE").replace("COE", "ZOE").replace("CA", "KA").replace("CA", "KA").replace("CO",
          "KO").replace("CU", "KU").replace("CE", "ZE").replace("CI", "ZI").replace("CY", "ZY").replace("F", "PH")




def is_acronym(strProbe, maxLength = 7, digitPlaceholder="Ð"):
    """
    Identifies Acronyms, restricted by absolute length
    "Ð" as default placeholder for digits. (e.g. "Ð")
    XXX look for "authoritative" definitions for acronyms
    :param strProbe:
    :param maxLength:
    :return:
    """
    if len(digitPlaceholder) > 1:
        print("Digit placeholders must be empty or a single character")
    ret = False
    s = strProbe.replace(digitPlaceholder, "0")
    l = 0
    u = 0
    if len(s) <= maxLength:
        for c in s:
            if c.isupper() == True: u = u + 1
            if c.islower() == True: l = l + 1
    if u > 1 and u > l: ret = True
    return ret


def simplify_german_string(strInGerman):
    """
    Decapitalises, substitutes umlauts, sharp s and converts k and z to c

    TODO ... explain why

    :param strInGerman:
    :return:
    """
    strInGerman = strInGerman.lower()
    strInGerman = strInGerman.replace("k", "c").replace("z", "c").replace("ß", "ss")
    strInGerman = strInGerman.replace("é", "e").replace("à", "a")
    return (strInGerman.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue"))


def diacritics():
    """
    TODO ... explain why

    :return: A string of diacritic characters
    """
    return ("µÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ")


def random_sub_list(inList, maxNum):
    """
    Generates random sublist.

    :param inList:
    :param maxNum:
    :return:
    """
    outList = []
    length = len(inList)
    if length <= maxNum: return inList
    c = 0
    rnumbers = []
    while (c < maxNum):
        rnumber = (randint(0, length - 1))
        if not rnumber in rnumbers:
            rnumbers.append(rnumber)
            c = len(rnumbers)
    for rnumber in rnumbers:
        outList.append(inList[rnumber])
    return outList


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
        strBin = str(bin(i))[2:].zfill(len(acro) - 1)
        bina.append(strBin.replace("0", "*|").replace("1", "*?|"))
    for expr in bina:
        lExp = expr.split("|")
        z = 0
        out = "^("
        for ex in lExp:
            out = out + acro[z] + "." + ex + ")("
            z = z + 1
        regs.append(out[0:-3] + "[A-Za-z" + dia + "0-9 ]*$)")
        # List of all regular expressions
        # print(regs)
        # print(fl)

    for reg in regs:
        if re.search(reg, fl, re.IGNORECASE) != None:
            result.append(re.findall(reg, fl, re.IGNORECASE)[0])
    return result


## Probes
# print(import_conf("NGRAMFILE"))
# print(CheckAcroVsFull("KHK", "koronare Herzkrankheit"))
# print(extractAcroDef("EKG (Elektrokardiogramm)", 7))
# print(extractAcroDef("Elektrokardiogramm", 7))
# print(extractAcroDef("Elektrokardiogramm (EKG)", 7))

def find_acro_expansions(lstNGramStat):
    """
    Identifies acronyms and looks for possible expansions.
    Takes the most frequent one.
    Uses ngrams with the second token being an acronym.

    TODO: check for what it is needed, complete it
    :param nGramStat: A list in which ngrams extracted
    from a corpus are counted in decreasing frequency

    :return:
    """

    dictCountPerNgram = {}
    lstAcro = [];
    lstNonAcro = []
    for line in lstNGramStat:
        ngram = line.split("\t")[1]
        count = line.split("\t")[0]
        dictCountPerNgram[ngram] = count
        if " " in ngram:  # has at least 2 tokens
            OtherTokens = " ".join(ngram.split(" ")[1:])
            if len(OtherTokens) > 2:
                if functions.isAcronym(OtherTokens[1], 7):
                    lstAcro.append(ngram)
                else:
                    for word in ngram.split(" "):
                        acro = False
                        if len(word) > 1:
                            if word[1].isupper() or not word.isalpha():
                                acro = True
                                break
                    if acro == False: lstNonAcro.append(ngram)

    for tk in lstAcro:
        counter = 0
        end = " ".join(tk.split(" ")[1:])
        regex = "^"
        for letter in end:
            # regex = regex + letter.upper() + ".*\s" # space required
            regex = regex + letter.upper() + ".*"  # no space required

        for t in lstNonAcro:
            endN = " ".join(t.split(" ")[1:])
            lastN = " ".join(t.split(" ")[-1])
            if t.split(" ")[0] == tk.split(" ")[0] and not t.split(" ")[1].upper() == tk.split(" ")[1].upper():
                if re.search(regex, endN.upper()):
                    if letter.upper() in lastN.upper():
                        print(tk + dictCountPerNgram[tk] + "     " + t + dictCountPerNgram[t])
                        counter += 1
                        if counter > 4:
                            break

# TODO michel 20180215 move to unit tests
# FindExpansionsOfAcronyms("corpus_cardio_ngramstat.txt")

print("Hello")