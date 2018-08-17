import os
import sys

import acres.evaluation.corpus
import acres.util.text

clear = lambda: os.system('cls')

# print(acres.rater.get_acronym_score("ICD", "Implantierbaren Defibrillator (ICD)"))
# print(acres.rater.get_acronym_score("ICD", "Implantierbaren Ca Defibrillator (ICD)"))
# print(acres.util.text.generate_all_variants_by_rules("Arterielle Verschlusskrankheit"))

# 1 / 0

acro = "KHK"
left = "de eine Koronarangiographie durchgeführt, dabei ¶ wurde eine"
right = "ausgeschlossen und eine hypertensive Herzkrankheit ¶ festges"

print(acres.rater.get_best_acronym_web_resolution(left, acro, right, 3, 7))

1 / 0
r = acres.evaluation.corpus.get_web_dump_from_acro_with_context(
    left, acro, right, 3, 6)

for t in r:
    s = acres.rater.get_acronym_score(acro, t[1])
    if s[1] > 0:
        print(str(t[0]) + "\t" + str(s[1]) + "\t" + s[0])

1 / 0

print(acres.rater.get_acronym_score("RR", "Blutdruck (RR)"))

1 / 0

# Hier Auflösung nur einmal und nur mit k
# r = acres.evaluation.corpus.get_web_dump_from_acro_with_context(
#    "   ulär getriggerte li.ventriculäre SM - ¶ Stimulatation. ¶¶ *",
#    "ICD",
#    "- Kontrolle ¶¶ Batterie Ð,Ð Jahre, Ladezeit Ð,Ðsec. ¶ Wahrn", 3, 6)

r = acres.evaluation.corpus.get_web_dump_from_acro_with_context(
    "Indikation zur ¶ primärprophylaktischen Versorgung mit einem",
    "ICD",
    "Aggregat gegeben. Da ¶ intermittierend ein Vorhofflimmern be", 3, 6)

# query = "GERD Adipositas"
query = "HDL Triglyceride"

# r = acres.web.get_web_ngram_stat.ngrams_web_dump("https://news.google.com/?hl=de", 1, 2)
# r = acres.web.get_web_ngram_stat.ngrams_web_dump("http://www.bing.de/search?cc=de&q=%22" + query + "%22", 1, 10)
# = acres.web.get_web_ngram_stat.ngrams_web_dump("http://www.bing.de/search?cc=de&q=" + query, 1, 10)
clear()
c = 0
for e in r:
    c = c + 1
    print(str(e[0]) + "\t" + e[1])
    # if c > 500:
    #    break

sys.exit()




if __name__ == "__main__":
    break_marker = "¶"
    text = """
    ----------
BEFUND
----------
 



* Anamnese

Pat. kommt heute zur vereinbarten Visite 2 im Rahmen der Dal-Studie. Der
Pat. gibt an, dass es ihm gut geht, keien AP, keine Dyspnoe., keine AE
oder SAE aufgetreten, keine Hospitalisierung seit der letzten Visite.
Keine Änderung der Begleitmedikaiton.
Der Pat. geht ab   morgen bis zum 8.9.2009 auf Reha in Bad X.

* Klinisch-physikalische Symptomatik

RR 160/82 Puls: 50
RR 161/82  Puös: 48
Gewicht: 84 kg, 178cm

* BEURTEILUNG

Der Pat.  erhält im Rahmen der DAL-outcome Studie Dalcetrapip.

* Die nächste Visite wurde für den 10.09.2019 für 8:00 Uhr vereinbart.

Bei Rückfragen    Tel:    0496/305 5544


---------
DIAGNOSEN
---------

I25.1 KHK I
I25.2 St. p. HW-Infarkt 2014
I10 art. Hypertonus
F17.1 Nikotinabusus
E79.0 HUK

-----------------
RELEVANTE BEFUNDE
-----------------


----------
MEDIKATION
----------

Exforge HCT 5/160/12,5mg 1-0-0
Folsan 5mg 1xpro Woche (Di)
Ferretab 1-1-0
Dalacin 300mg 1-1-1bis einschl. 20.04.2020"""

    text = acres.util.text.fix_line_endings(text, break_marker)

    text = text.replace(break_marker, " " + break_marker + " ")
    text = acres.util.text.reduce_repeated_chars(text, " ", 1)
    text = text.replace(break_marker + " " + break_marker, break_marker + break_marker)
    text = text.replace(break_marker + " " + break_marker, break_marker + break_marker)
    text = acres.util.text.reduce_repeated_chars(text, break_marker, 2)

    print(text)
    print(text.replace(break_marker, break_marker + "\n"))
