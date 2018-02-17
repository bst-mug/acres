# import ling
import re
from acres import functions


def FindExpansionsOfAcronyms(lstNGramStat):
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
    lstAcro = [] ;  lstNonAcro = []
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
