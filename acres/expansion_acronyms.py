# import ling
import re
from acres import functions


def find_acronym_expansion(lst_ngam_stat):
    """
    Identifies acronyms and looks for possible expansions.
    Takes the most frequent one.
    Uses ngrams with the second token being an acronym.

    TODO: check for what it is needed, complete it
    :param lst_ngam_stat: A list in which ngrams extracted
    from a corpus are counted in decreasing frequency

    :return:
    """

    dict_count_per_ngram = {}
    lstAcro = []
    lstNonAcro = []
    acro = False
    # TODO: check initialization of acro
    for line in lst_ngam_stat:
        ngram = line.split("\t")[1]
        count = line.split("\t")[0]
        dict_count_per_ngram[ngram] = count
        if " " in ngram:  # has at least 2 tokens
            OtherTokens = " ".join(ngram.split(" ")[1:])
            if len(OtherTokens) > 2:
                if functions.is_acronym(OtherTokens[1], 7):
                    lstAcro.append(ngram)
                else:
                    for word in ngram.split(" "):
                        acro = False
                        if len(word) > 1:
                            if word[1].isupper() or not word.isalpha():
                                acro = True
                                break
                    if not acro:
                        lstNonAcro.append(ngram)

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
            if t.split(" ")[0] == tk.split(" ")[0] and not t.split(
                    " ")[1].upper() == tk.split(" ")[1].upper():
                if re.search(regex, endN.upper()):
                    if letter.upper() in lastN.upper():
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
