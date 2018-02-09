# This module "ling" contains functions that manipulate and
# interpret strings

# Stefan Schulz 20150517
# Create a dictionary that counts each nGram
# in an input string. Delimiters are spaces
# Example: bigrams and trigrams
# nMin = 2 ,   nMax = 3
# PROBE: # print(WordNgramStat('a ab aa a a a ba ddd', 1, 4))
#
def WordNgramStat(InputString, nMin, nMax):
    output = {}
    lines = InputString.splitlines()
    for line in lines:
        line = line.replace('\r', '')
        line = line.replace('\n', '')
        line = line.strip()
        input = line.split(" ")
        for n in range(nMin, nMax + 1):
            for i in range(len(input) - n + 1):
                g = ' '.join(input[i:i+n])
                output.setdefault(g,0)
                output[g] +=1
#    Example for formatted output, sorted, reverse order
#    for w in sorted(output, key=output.get, reverse = True):
#       print ('{:>8}'.format(output[w]) + '\t' + w)
    return output

def WordWithCaseStat(InputString, nMin, nMax):
    output = {}
    lines = InputString.splitlines()
    for line in lines:
        line = line.replace('\r', '')
        line = line.replace('\n', '')
        line = line.strip()
        input = line.split(" ")
        for n in range(2, 3):
            for i in range(len(input) - n + 1):
                g = ' '.join(input[i:i+n])
                output.setdefault(g,0)
                output[g] +=1
#    Example for formatted output, sorted, reverse order
#     for w in sorted(output, key=output.get, reverse = True):
#       print ('{:>8}'.format(output[w]) + '\t' + w)
    return output


def GermanToSevenBitNormalisedText(strIn):
    return strIn.upper().replace("À", "A").replace("Á", "A").replace("Â", "A").replace("Ã", "A").replace("Ä", "AE").replace("Å", "AA").replace("Æ", "AE").replace("Ç", "C").replace("È", "E").replace("É", "E").replace("Ê", "E").replace("Ë", "E").replace("Ì", "I").replace("Í", "I").replace("Î", "I").replace("Ï", "I").replace("Ñ", "N").replace("Ò", "O").replace("Ó", "O").replace("Ô", "O").replace("Õ", "O").replace("Ö", "OE").replace("Ø", "OE").replace("Ù", "U").replace("Ú", "U").replace("Û", "U").replace("Ü", "UE") 
    
def GermanNormalisedClinicalText(strIn):
    import ling
    #no Acronym
    if len(strIn) == 1:
        return strIn.isupper()
    if len(strIn) == 2 and strIn[1].isupper():
        return strIn
    if strIn[2].isupper():
        return strIn
    strIn = ling.GermanToSevenBitNormalisedText(strIn) 
    return strIn.replace("CAE", "ZAE").replace("COE", "ZOE").replace("CA", "KA").replace("CA", "KA").replace("CO", "KO").replace("CU", "KU").replace("CE", "ZE").replace("CI", "ZI").replace("CY", "ZY").replace("F", "PH")                      
 


#print(WordNgramStat('a ab aa a a a ba ddd', 1, 4))



