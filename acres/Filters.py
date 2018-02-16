# Stefan Schulz 28 May 2017

 
import re
from acres import Functions
import pickle


def bestAcronymResolution(shortForm, candidates, tokenlist, shortformtype, context):
    """
    Scores candidate acronym resolutions using a n-gram frequency list from related corpus.

    :param shortForm:
    :param candidates:
    :param tokenlist:
    :param shortformtype:
    :param context:
    :return:
    """
    if shortformtype == "AA":
        regexAcro = ""
        out = []
        shortForm = shortForm.replace(".", "").replace("-", "").replace("/", " ")
        for c in shortForm:
            regexAcro = regexAcro + c + ".*"
            regexAcro = "^" + regexAcro      
        for row in candidates:
            ngram = row.split("\t")[1]
            print(ngram)
            m = re.search(regexAcro, ngram, re.IGNORECASE)
            if m != None and not shortForm in ngram:
                segmL = Functions.CheckAcroVsFull(shortForm, ngram)
                    # returns list like [[('Elektro', 'kardio', 'gramm')],
                    # [('Elektro', 'kardio', 'gramm')], [('Ele', 'ktrokardio', 'gramm')],
                    # [('Ele', 'ktrokardio', 'gramm')]]
                maxScore = 0
                summ = 0
                for segms in segmL: 
                    summ = 0 
                    for seg in segms:                   
                        seg = seg.strip()
                        if seg in tokenlist: summ +=1
                    if summ > maxScore: maxScore = summ
                out.append('{:0>2}'.format(str(maxScore))+ "\t" + ngram)
        out.sort(reverse=True)
        return out
                
#normalisedTokens = pickle.load(open("tokens.p", "rb"))
#print(bestAcronymResolution("SR", ['123\tSinusrhythmus', '123\tSinusarrhytmie', '123\tkein Sinusrh.' ], normalisedTokens, "AA", ""))
            
 
