"""Experiments

This module extracts acronyms in context from
Text and Training files


"""
import logging
import random

from acres import functions

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def extract_acronym_with_context(text, window):
    l_tok = text.split(" ")
    char_count = 0
    out = ""
    for t in l_tok:
        char_count = char_count + len(t) + 1
        a = ""
        # we take also those followed by dash
        if "-" in t:
            if functions.is_acronym(t.split("-")[0], 7):
                a = t
        if functions.is_acronym(t, 7):
            a = t
        if a != "":
            out = out + text[char_count - window - len(a) - 2: char_count - len(a) - 2] + "\t" + a + "\t"
            out = out + text[char_count:char_count + window] + "\n"

    return out


probe = """* Anamnese und klin. Symptomatik

Der Patient ist am 18.03.2010 bei K&Ö aus völligem WBF heraus zusammengebrochen, beobachtet durch den SOHN. Es erfolgte eine Laienreanimation durch eine zufällig anwesende praktische Ärztin (HDM, keine Beatmung), dann Übernahme durch den Notarzt, 35 min bis erstmal ROSC, multiple VF/VT/Defibrillation. Im Erst- EKG zeigte sich eine Hebung in I, aVL, V4 bis V6 im Sinne eines STEMI des Vorderwandinfarktes. Nach der Lyse waren die Hebungen deutlich rückläufig und hämodynamisch ohne Katecholamine stabil. Daher wurde der Patient initial ad die CCU transferiert. * Physikalischer Status
"""


# print(extract_acronym_with_context(probe, 30))


def get_acronym_sample():
    #output_file = "C:\\Users\\SchulzS\\PycharmProjects\\acres\\resources\\" + "acrosample.txt"
    output_file = "resources/acrosample.txt"

    # corpus_path = "S:\\DocumentCleansing\\CardioCorpusSplit\\Temp"
    corpus_path = functions.import_conf("CORPUS_PATH")

    # sample_size = 100
    # window_size = 500
    sampling_rate = 100

    digit_placeholder = "Ð"
    break_marker = "¶"
    entire_corpus = ""
    counter = 0
    texts = functions.robust_text_import_from_dir(corpus_path)
    l = len(texts)
    print("Loaded %d texts.", l)
    for text in texts:
        r = random.randint(1, sampling_rate)
        if counter % r == 0:
            print(counter)
            text = functions.fix_line_endings(text, break_marker)

            if len(digit_placeholder) == 1:
                text = functions.clear_digits(text, digit_placeholder)
            text = text.replace("  ", " ").replace("  ", " ")
            text = text.replace("\n", " ")
            text = text.replace(break_marker, " " + break_marker + " ")
            text = text.replace("  ", " ").replace("  ", " ")
            entire_corpus = entire_corpus + text + "\n"
            counter += 1

    print("Corpus loaded containing %d documents.", counter)
    print("Corpus contains %d characters", len(entire_corpus))
    cL = entire_corpus.split("\n")
    out = ""
    for text in cL:
        out = out + extract_acronym_with_context(text, 60)
    g = open(output_file, "w", encoding="utf-8")
    g.write(out)
    g.close()


get_acronym_sample()
