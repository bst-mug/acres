# import ling
# import dump
import re


def FindExpansionsOfAcronyms(TokenStat):
    """
    Identifies acronyms and looks for possible expansions.
    Takes the most frequent one.
    Uses ngrams with the second token being an acronym.

    :param TokenStat: some description
    :return:
    """

    d = {}
    Acronyms = []
    NonAcronyms = []

    # FIXME NameError: name 'dump' is not defined
    # lines = dump.ToList(TokenStat)
    lines = []
    for line in lines:
        phrase = line.split("\t")[1]
        count = line.split("\t")[0]
        d[phrase] = count
        if " " in phrase:  # has at least 2 tokens
            OtherTokens = " ".join(phrase.split(" ")[1:])
            if len(OtherTokens) > 2:
                if OtherTokens[1].isupper() and OtherTokens.isalpha() and len(OtherTokens) <= 6:
                    Acronyms.append(phrase)
                else:
                    for word in phrase.split(" "):
                        acro = False
                        if len(word) > 1:
                            if word[1].isupper() or not word.isalpha():
                                acro = True
                                break
                    if acro == False:
                        NonAcronyms.append(phrase)

    for tk in Acronyms:
        print(tk)
        z = 0
        end = " ".join(tk.split(" ")[1:])
        reg = "^"
        for letter in end:
            # reg = reg + letter.upper() + ".*\s" # space required
            reg = reg + letter.upper() + ".*"  # no space required

        for t in NonAcronyms:
            endN = " ".join(t.split(" ")[1:])
            lastN = " ".join(t.split(" ")[-1])
            if t.split(" ")[0] == tk.split(" ")[0] and not t.split(" ")[1].upper() == tk.split(" ")[1].upper():
                if re.search(reg, endN.upper()):
                    if letter.upper() in lastN.upper():
                        print(tk + d[tk] + "     " + t + d[t])
                        z = z + 1
                        if z > 4:
                            break

# TODO michel 20180215 move to unit tests
# FindExpansionsOfAcronyms("corpus_cardio_ngramstat.txt")
