# code for benchmarking
import logging
from logging.config import fileConfig

from acres import get_synonyms_from_ngrams

logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# actual = get_synonyms_from_ngrams.find_embeddings("*", "TRINS", "*", 1, 2, 500, 1, 10)

f = open("resources/Workbench.txt", "r", encoding="utf-8")
# sRow = input("Select row number or press enter: ")
# the Workbench now contains the records like in Excel table, separated by tabs



for row in f:
    out = ""
    if row != "":
        row = row.strip("\n")
        logger.info("=======================")
        logger.info("Analyzing: " + row)
        logger.info("=======================")
        le = len(row.split("\t"))
        # row_nr = row.split("\t")[0]
        left_context = row.split("\t")[0]
        acro = row.split("\t")[1]
        right_context = row.split("\t")[2]
        l_probe = row.split("\t")[3:]

        l_left = left_context.split(" ")[-3:]
        l_right = right_context.split(" ")[:3]
        # TO DO tentative
        if left_context != "":
            le = " ".join(l_left[-1:])
            lele = " ".join(l_left[-2:])
            lelele = " ".join(l_left[-3:])
        else:
            le = "<SEL>"
            lele = "<SEL>"
            lelele = "<SEL>"

        if right_context != "":
            re = " ".join(l_right[:1])
            rere = " ".join(l_right[:2])
            rerere = " ".join(l_right[:3])
        else:
            re = "<SEL>"
            rere = "<SEL>"
            rerere = "<SEL>"

        l_patterns = [(lelele, rerere), (lele, rerere), (lelele, rere), (lele, rere),
                      (le, rere), (lele, re), (le, re), (lele, "<SEL>"), (le, "<SEL>"),
                      ("<SEL>", rere), ("<SEL>", re), ("<SEL>", "<SEL>"),
                      ("<SEL>", "<VOID>"), ("<VOID>", "<SEL>")]

        l_prev = ""
        r_prev = ""
        for patt in l_patterns:
            if not (patt[0] == l_prev and patt[1] == r_prev):
                v = get_synonyms_from_ngrams.test_input(l_probe, patt[0], acro, patt[1])
                print(patt)
                if v == True:
                    print("FOUND")
                    break

                l_prev = patt[0]
                r_prev = patt[1]

f.close()
