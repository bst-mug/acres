import logging
import re

from acres import functions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def find_best_substitution(form_to_resolve, candidates,
                           lst_tokens, short_form_type):
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
    HA: hyphen abbreviations like "Roe-Thorax"
    MA: multiword abbreviations like "St. p."
    SE_ spelling errors like "Lympfknoten"


    :param form_to_resolve:
    :param candidates:
    :param lst_tokens:
    :param short_form_type:
    :return:
    """
    if short_form_type == "AA":
        regex_acro = ""
        out = []
        form_to_resolve = form_to_resolve.replace(
            ".", "").replace("-", "").replace("/", " ")
        for c in form_to_resolve:
            regex_acro = regex_acro + c + ".*"
            regex_acro = "^" + regex_acro
        for row in candidates:
            ngram = row.split("\t")[1]
            print(ngram)
            m = re.search(regex_acro, ngram, re.IGNORECASE)
            if m is not None and form_to_resolve not in ngram:
                segmL = functions.check_acro_vs_expansion(form_to_resolve, ngram)
                # returns list like [[('Elektro', 'kardio', 'gramm')],
                # [('Elektro', 'kardio', 'gramm')], [('Ele', 'ktrokardio', 'gramm')],
                # [('Ele', 'ktrokardio', 'gramm')]]
                max_score = 0
                summ = 0
                for segms in segmL:
                    summ = 0
                    for seg in segms:
                        seg = seg.strip()
                        if seg in lst_tokens:
                            summ += 1
                    if summ > max_score:
                        max_score = summ
                out.append('{:0>2}'.format(str(max_score)) + "\t" + ngram)
        out.sort(reverse=True)
        return out

# normalisedTokens = pickle.load(open("tokens.p", "rb"))
# print(bestAcronymResolution("SR", ['123\tSinusrhythmus', '123\tSinusarrhytmie', '123\tkein Sinusrh.' ], normalisedTokens, "AA", ""))
