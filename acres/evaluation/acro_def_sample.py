###
### Metrics from large German acronym / definition list
###
###

import acres.util.acronym
import acres.util.functions


def dump_sample(min_len=1, max_len=15):
    ret = []
    f = open("resources/acro_full_reference.txt", "r", encoding="utf-8")
    for l in f:
        acro = l.split("\t")[0]
        if len(acro) >= min_len and len(acro) <= max_len:
            ret.append(l.strip())
    f.close()
    return ret


def show_extremes(txt, lst, lowest_n, highest_n):
    if len(lst) <= lowest_n + highest_n:
        print("List too small")
    else:
        print("\n==========================================")
        print(txt)
        print("==========================================\n")
        c = 0
        for i in sorted(lst):
            print(i)
            c = c + 1
            if c >= lowest_n:
                break
        print("(...)")
        c = 0
        for i in sorted(lst, reverse=True):
            print(i)
            c = c + 1
            if c >= lowest_n:
                break


def run_tests()

    r = dump_sample(3, 3)
    for l in r:
        acro = l.split("\t")[0].strip()
        full = l.split("\t")[1].strip()
        if not acres.util.acronym.is_acronym(acro):
            print(acro + " is not an acronym according to our definition")
        if full.count(" ") + 1 > len(acro) * 2:
            print(acro + " contradicts Schwartz / Hearst rule")
        if full.count(" ") + 1 > len(acro) + 5:
            print(acro + " contradicts Schwartz / Hearst rule")

    l_count = []  ## ratio acro / words
    for l in r:
        acro = l.split("\t")[0]
        full = l.split("\t")[1]
        full_norm = full.replace("/", " ").replace("-", " ").replace("  ", " ").strip()
        c_words_full = full_norm.count(" ") + 1
        c_chars_acro = len(acro)
        rat = round(c_chars_acro / c_words_full, 2)
        l_count.append((rat, acro, full))

    show_extremes("Ratio acronym length / words in full form", l_count, 10, 10)

    l_count = []  ## edit distance with generated acronym
    for l in r:

        acro = l.split("\t")[0]
        full = l.split("\t")[1]
        if abs(len(acro) - full.count(" ") - 1) <= 2:
            n_acro = acres.util.acronym.create_german_acronym(full)
            lev = acres.util.functions.Levenshtein(acro.upper(), n_acro)
            l_count.append((lev, acro, full))

    show_extremes("edit distance with generated acronym", l_count, 10, 10)
