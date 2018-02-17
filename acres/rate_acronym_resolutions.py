# Stefan Schulz 11 Nov 2017


import pickle
import re
import logging

# from math import *
from acres import functions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG) # Uncomment this to get debug messages


def GetAcronymScore(acro, full, sMorph):
    """
    Scores Acronym / resolution pairs according to a series of well-formedness criteria using a n-gram frequency list
    from related corpus.

    Scoring is higher the better the full form is properly split into morphemes.
    Requires identification and removal of Affixes (infixes, suffixes, like "Gastr-o", "Schmerz-en").

    :param acro:
    :param full:
    :param sMorph:
    :return:
    """
    score = 1  # standard score
    pen = 1  # penalization factor
    acro = acro.strip()
    full = full.strip()
    # XXX Dependent on German medical language
    lAffixDeOne = ["a", "e", "i", "n", "o", "s", ]
    lAffixDeTwo = ["ae", "en", "er", "em", "es", "is", "um", "us"]
    # full form contains an acronym definition pattern (normally only yielded from Web scraping)
    ret = functions.extract_acronym_definition(full, 7)
    if ret != None:
        if ret[0] == acro:
            full = ret[1]
            score = 100  # return???
    # acronym must have at least two characters
    if len(acro) < 2: return 0
    # length restriction for full form
    if len(full) < 3: return 0
    # acronym must not occur within full form
    if acro in full: return 0  # Check A
    # for each acronym in full form, penalisation
    # TODO: check if artefact
    for t in acro.split(" "):  # FIXME should be full.split??
        if functions.is_acronym(t, 7): pen = pen / 4
    # Plural form of acronym reduced to singular ("s", often not found in non English full forms)
    # e.g. "EKGs", "EKGS", "NTx", "NTX" (Nierentransplantation)
    # These characters cannot be always expected to occur in the full form
    # We assume that plurals and genitives of acronyms are always marked with lower case "s"
    if (acro[-1] == "s" or acro[-1] == "x" or acro[-1] == "X") and acro[-2:-1].isupper():
        acro = acro[0:-1]
    # relative length, cf.
    # SCHWARTZ, Ariel S.; HEARST, Marti A. A simple algorithm for identifying abbreviation
    # definitions in biomedical text. In: Biocomputing 2003. 2002. S. 451-462.
    if full.count(" ") + 1 > len(acro) * 2: return 0
    if full.count(" ") + 1 > len(acro) + 5: return 0
    acroL = acro.lower()
    fullL = full.lower()
    # decapitalized acronym must not occur within decap full form,
    # if acronym has three or more letters
    if acroL in fullL and len(acroL) > 2: return 0  # TODO unify with the check A
    # first chars must be the same
    if acroL[0] != fullL[0]: return 0
    # last char of acronym must occur in last word of full
    # but not at the end unless it is a single letter
    # "EKG" = "Enttwicklung" should not match
    # "Hepatitis A" -> "HEPA" should match
    lastWord = fullL.split(" ")[-1]
    if len(lastWord) == 1 and acroL[-1] != lastWord: return 0
    if not acroL[-1] in lastWord[0:-1]: return 0
    # for each word in full higher than length of acronym, penalisation factor (square)
    if len(acroL) < fullL.count(" ") + 1:
        pen = 1 / ((fullL.count(" ") + 1 - len(acroL)) * 2)  # TODO does not use previous penalization factor
        # print("Penalization = " + str(pen))
    # Extract upper case sequence from full form
    expUpp = ""
    if full.count(" ") > 0:
        lTok = full.split(" ")
        for tok in lTok:
            if tok > " ":
                if tok[0].isupper(): expUpp = expUpp + tok[0] + ".*"
    expUpp = expUpp.upper()  # FIXME not needed?
    # if upper case word initial is not represented in the acronym, then
    # penalisation
    if re.search(expUpp, acro) == None:
        pen = pen * 0.25  # FIXME: check whether right

    # FIXME duplicate code at functions.CheckAcroVsFull()
    dia = functions.diacritics()
    bina = []
    splits = []
    fl = ""
    # remove most punctuation chars from full
    # tokenization, preserving hyphen or chars in acro
    for c in fullL:
        if c.isalnum() or c in " -" or c in acroL:
            fl = fl + c
        else:
            fl = fl + " "
    fl = fl.strip()
    # list of binary combinations of alternative regex patterns
    # (greedy vs. non-greedy)
    regs = []  # list of alternative regular expressions
    # XXX: state machines instead of Regex
    # XXX: debug what happens with "TRINS" - "Trikuspidalinsuffizienz"
    # XXX: correct segmentation: 't', 'ricuspidal', 'i', 'n', 'suffizienz'
    # XXX: obvious morpheme-based scoring does not work well
    # XXX with this unorthodox building patterns
    for i in range(0, (2 ** (len(acroL) - 1))):
        strBin = str(bin(i))[2:].zfill(len(acroL) - 1)
        logger.debug(strBin)
        bina.append(strBin.replace("0", "*|").replace("1", "*?|"))
    for expr in bina:
        lExp = expr.split("|")
        z = 0
        out = "^("
        for ex in lExp:
            out = out + re.escape(acroL[z]) + "." + ex + ")("
            z = z + 1
        regs.append(out[0:-3] + "[A-Za-z" + dia + "0-9 ]*$)")
    for reg in regs:
        # print(reg)
        if re.search(reg, fl, re.IGNORECASE) != None:
            splits.append(re.findall(reg, fl, re.IGNORECASE)[0])
    # END of duplicate code

    score = 0
    logger.debug(splits)
    for split in splits:
        s = 0
        for fragment in split:
            # !!!! Specific for German
            #TODO : check whether the function  substitute_k_and_f_by_context
            #TODO : could be used instead (produces 7-Bit string without K and F)
            fragment = functions.simplify_german_string(fragment).strip()
            # C, K, and Z no longer distinguished
            # XXX Soundex as an alternative ??
            logger.debug("FR: " + fragment)
            # Check whether fragments are in german / english morpheme list
            # From Morphosaurus
            if fragment in sMorph or len(fragment) == 1:
                s = s + 1
            else:
                if (len(fragment) > 2) and (fragment[-1] in lAffixDeOne) and (fragment[0:-1] in sMorph):
                    # stripping one character suffix or infix
                    logger.debug(fragment[0:-1])
                    s = s + 1
                else:
                    if (len(fragment)) > 3 and (fragment[-2:] in lAffixDeTwo) and (fragment[0:-2] in sMorph):
                        # stripping two character suffix
                        logger.debug(fragment[0:-2])
                        s = s + 1
        if s / len(split) > score:
            score = s / len(split)
            if score == 0: score = 0.01
            score = score * pen
    return (score)


def get_acronym_score(acronym, full_form):
    """
    Syntactic sugar for GetAcronymScore(acro, full, sMorph)

    :param acronym:
    :param full_form:
    :return:
    """
    # TODO generate pickle if not available
    # TODO make it work even without morphemes?
    morphemes = pickle.load(open("models/pickle/morphemes.p", "rb"))
    return GetAcronymScore(acronym, full_form, morphemes)
