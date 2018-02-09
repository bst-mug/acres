## Python 3
## Module with functions for
## Corpus analyssis

# This function compares and acronym
# with a potential full form and
# returns a list of segmentations
# Stefan Schulz, 18 Mar 2017

import time
from random import randint

def splitNgram(ngram):
# Splits a token ngram with acronym(s) into all combinations of
# left - acro - token
        out = []
        lTokens = ngram.split(" ")
        c = 0
        for t in lTokens:
            if isAcronym(t, 7):
                tr = (" ".join(lTokens[0:c]), lTokens[c], " ".join(lTokens[c + 1:]))
                out.append(tr)
            c = c + 1
        return out


def extractAcroDef(strProbe, maxLength):
    # identifies potential acronym / definition pairs and 
    # extract acronym and definition candidates
    strProbe = strProbe.strip()
    if len(strProbe) > 1:
        if strProbe[-1] == ")" and strProbe.count("(") == 1:
            left = strProbe.split("(")[0].strip()
            right = strProbe.split("(")[1][0:-1].strip()
            if isAcronym(left, maxLength) and not isAcronym(right, maxLength):
                return(left, right)
            if isAcronym(right, maxLength) and not isAcronym(left, maxLength):
                return(right, left)
            
        

def isAcronym(strProbe, maxLength):
    # identifies Acronyms, restricted by absolute length
    # depends on "Ð" as a placeholder for digits
    # XXX look for "authoritative" definitions for acronyms
    ret = False
    s = strProbe.replace("Ð", "0")
    l = 0
    u = 0
    if len(s) <= maxLength:  
        for c in s:
            if c.isupper() == True: u = u + 1
            if c.islower() == True: l = l + 1
    if u > 1 and u > l: ret = True
            
    return ret

def simplifyGermanString(strInGerman):
    # decapitalises, substitutes umlauts,
    # sharp s and converts k and z to c
    strInGerman = strInGerman.lower()
    strInGerman = strInGerman.replace("k", "c").replace("z", "c").replace("ß", "ss")
    strIngerman = strInGerman.replace("é", "e").replace("à", "a")
    return(strInGerman.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue"))

def diacritics():
    # returns a string of diacritic characters
    return ("µÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ")
 

def randomSubList(inList, maxNum):
    # Generates random sublist
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
    dia = Functions.diacritics()
    aLeft = acro[0:-1]
    aRight = acro [-1]
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
    regs = [] # list of alternative regular expressions
    for i in range(0, (2**(len(acro) -1))):
        strBin = str(bin(i))[2:].zfill(len(acro) -1)
        bina.append(strBin.replace("0", "*|").replace("1", "*?|"))
    for expr in bina:
        lExp = expr.split("|")
        z = 0
        out = "^("
        for ex in lExp:
            out = out + acro[z] + "." + ex + ")("
            z = z + 1
        regs.append(out[0:-3] + "[A-Za-z" + DIACRITICS + "0-9 ]*$)")
        #List of all regular expressions
        #print(regs)
        #print(fl)

    for reg in regs:
        if re.search(reg, fl, re.IGNORECASE) != None:
            result.append(re.findall(reg, fl, re.IGNORECASE)[0])
    return result

## Probes
print(isAcronym("5FU", 7))
#print(CheckAcroVsFull("KHK", "koronare Herzkrankheit"))
#print(extractAcroDef("EKG (Elektrokardiogramm)", 7))
#print(extractAcroDef("Elektrokardiogramm", 7))
#print(extractAcroDef("Elektrokardiogramm (EKG)", 7))
