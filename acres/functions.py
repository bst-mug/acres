# Stefan Schulz, 18 Mar 2017
"""
Module with functions for corpus analysis.

TODO move to proper function
This function compares and acronym with a potential full form and returns a list of segmentations.
"""

import configparser
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


def splitNgram(ngram):
    """
    Splits a token ngram with acronym(s) into all combinations of left - acro - token.

    :param ngram:
    :return:
    """
    out = []
    lTokens = ngram.split(" ")
    c = 0
    for t in lTokens:
        if isAcronym(t, 7, "Ð"):
            tr = (" ".join(lTokens[0:c]), lTokens[c], " ".join(lTokens[c + 1:]))
            out.append(tr)
        c = c + 1
    return out


def extractAcroDef(strProbe, maxLength):
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
            if isAcronym(left, maxLength, "Ð") and not isAcronym(right, maxLength, "Ð"):
                return (left, right)
            if isAcronym(right, maxLength, "Ð") and not isAcronym(left, maxLength, "Ð"):
                return (right, left)


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
        input = line.split(" ")
        for n in range(nMin, nMax + 1):
            for i in range(len(input) - n + 1):
                g = ' '.join(input[i:i + n])
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




def isAcronym(strProbe, maxLength = 7, digitPlaceholder="Ð"):
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


def simplifyGermanString(strInGerman):
    """
    Decapitalises, substitutes umlauts, sharp s and converts k and z to c

    TODO ... explain why

    :param strInGerman:
    :return:
    """
    strInGerman = strInGerman.lower()
    strInGerman = strInGerman.replace("k", "c").replace("z", "c").replace("ß", "ss")
    strIngerman = strInGerman.replace("é", "e").replace("à", "a")
    return (strInGerman.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue"))


def diacritics():
    """
    TODO ... explain why

    :return: A string of diacritic characters
    """
    return ("µÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ")


def randomSubList(inList, maxNum):
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


def CheckAcroVsFull(acro, full):
    import re
    dia = diacritics()
    aLeft = acro[0:-1]
    aRight = acro[-1]
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

print(isAcronym("5-FU", 7))
print(isAcronym("5-FU"))
print(isAcronym("5-FU", 7, "we"))
