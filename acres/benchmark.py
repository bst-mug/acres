# code for benchmarking
import logging

from acres import get_synonyms_from_ngrams

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# actual = get_synonyms_from_ngrams.find_embeddings("*", "TRINS", "*", 1, 2, 500, 1, 10)

f = open("resources/Workbench.txt", "r", encoding="utf-8")
# sRow = input("Select row number or press enter: ")
for row in f:
    out = ""
    if row > " ":
        row = row.strip("\n")
        logger.info("=======================")
        logger.info("Analyzing: " + row)
        logger.info("=======================")
        row_nr = row.split("|")[0]
        left_context = row.split("|")[1]
        acro = row.split("|")[2]
        right_context = row.split("|")[3]
        probe = row.split("|")[4]

        v = get_synonyms_from_ngrams.test_input(probe, left_context, acro, right_context)
        if v == True:
            out = out + "<DEF> <ACR> <DEF>: Found"
        else:
            out = out + "<DEF> <ACR> <DEF>: Not Found\n"
            v = get_synonyms_from_ngrams.test_input(probe, "<SEL>", acro, right_context)
            if v == True:
                out = out + "<SEL> <ACR> <DEF>: Found"
            else:
                out = out + "<SEL> <ACR> <DEF>: Not Found\n"
                v = get_synonyms_from_ngrams.test_input(probe, left_context, acro, "<SEL>")
                if v == True:
                    out = out + "<DEF> <ACR> <SEL>: Found"
                else:
                    out = out + "<DEF> <ACR> <SEL>: Not Found\n"
                    v = get_synonyms_from_ngrams.test_input(probe, "<SEL>", acro, "<SEL>")
                    if v == True:
                        out = out + "<SEL> <ACR> <SEL>: Found"
                    else:
                        out = out + "<SEL> <ACR> <SEL>: Not Found\n"
                        v = get_synonyms_from_ngrams.test_input(probe, "<VOID>", acro, "<SEL>")
                        if v == True:
                            out = out + "<VOID> <ACR> <SEL>: Found"
                        else:
                            out = out + "<VOID> <ACR> <SEL>: Not Found\n"
                            v = get_synonyms_from_ngrams.test_input(probe, "<SEL>", acro, "<VOID>")
                            if v == True:
                                out = out + "<SEL> <ACR> <VOID>: Found"
                            else:
                                out = out + "<SEL> <ACR> <VOID>: Not Found"
    print("Final analysis: " + row)
    print(out)

f.close()
