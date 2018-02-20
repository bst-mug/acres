import logging
import re

from acres import functions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG) # Uncomment this to get debug messages

def find_best_substitution(formToResolve, candidates,
                           tokenlist, shortformtype, context):
    """
    This will eventually be the master function invoked by the text cleansing process
    Finds the best resolution of a nonlexicalised form
    using a n-gram frequency list from related corpus.
    TODO:    This includes all tokens and ngrams for which a language model is expected to
    TODO:    yield the right expansion

    Tentative Typology :
    AA: classical acronyms like "EKG"
    DA: dot abbreviations like "diff."
    NA: non-dot abbreviations like "re"
    HA: hyphen abbreviations like "Rö-Thorax"
    MA: multiword abbreviations like "St. p."
    SE_ spelling errors like "Lympfknoten"


    :param formToResolve:
    :param candidates:
    :param tokenlist:
    :param shortformtype:
    :param context:
    :return:
    """
    if shortformtype == "AA":
        regexAcro = ""
        out = []
        formToResolve = formToResolve.replace(
            ".", "").replace("-", "").replace("/", " ")
        for c in formToResolve:
            regexAcro = regexAcro + c + ".*"
            regexAcro = "^" + regexAcro
        for row in candidates:
            ngram = row.split("\t")[1]
            logger.debug(ngram)
            m = re.search(regexAcro, ngram, re.IGNORECASE)
            if m is not None and formToResolve not in ngram:
                segmL = functions.check_acro_vs_expansion(formToResolve, ngram)
                # returns list like [[('Elektro', 'kardio', 'gramm')],
                # [('Elektro', 'kardio', 'gramm')], [('Ele', 'ktrokardio', 'gramm')],
                # [('Ele', 'ktrokardio', 'gramm')]]
                maxScore = 0
                summ = 0
                for segms in segmL:
                    summ = 0
                    for seg in segms:
                        seg = seg.strip()
                        if seg in tokenlist:
                            summ += 1
                    if summ > maxScore:
                        maxScore = summ
                out.append('{:0>2}'.format(str(maxScore)) + "\t" + ngram)
        out.sort(reverse=True)
        return out

# normalisedTokens = pickle.load(open("tokens.p", "rb"))
# logger.debug(bestAcronymResolution("SR", ['123\tSinusrhythmus', '123\tSinusarrhytmie', '123\tkein Sinusrh.' ], normalisedTokens, "AA", ""))
