import os
import sys

import acres.preprocess.resource_factory
from acres.web import base

clear = lambda: os.system('cls')

# print(acres.rater.rater.get_acronym_score("ICD", "Implantierbaren Defibrillator (ICD)"))
# print(acres.rater.rater.get_acronym_score("ICD", "Implantierbaren Ca Defibrillator (ICD)"))
# print(acres.util.text.generate_all_variants_by_rules("Arterielle Verschlusskrankheit"))


if 1 == 1:
    # TODO: "Operation" does not appear in list!

    acro = "ED"
    left = "Patienten mit"
    right = "die eine arterielle koronare Verschlusskrankheit"

    acro = "OP"
    left = "beim Hausarzt auf. Bitte diesbezüglich sämtliche Befunde zur"
    right = "mitnehmen. ¶ Für den Eingriff Thrombo-ASS und Plavix keinesf"

    acro = "LV"
    left = "¶ li.Vorhof mit ÐÐ mm mittelgradig vergrößert, RA und"
    right = "groß, ¶ Aortenklappensklerose ohne signifikante Steno"

    acro = "NINS"
    left = "beginnende KHK ¶ NÐÐ.Ð Dialysepflichtige"
    right = "IDDM(seit über ÐÐ Jahren)"

    acro = "NYHA"
    left = "Kardiologie Ambuzlanz erfolgte bei ¶ Belastungsdyspnoe"
    right = "III mit zunehmender Leistungsminderung"

    # not found => wrong suggestion
    acro = "PAP"
    left = "einem maximalen Gradienten ¶ von ÐÐmmHg.entsprechend einem"
    right = "von rund ÐÐmmHg., kein    Pericarderguss"

    # TODO: This example does not terminate
    acro = "US-Ödemen"
    left = "abnehmend, sowie das Auftreten von deutlichen"
    right = "ohne"

    # not found ("Ultraschallkardiogramm" is rather uncommon)
    acro = "USKG"
    left = "ein      Aortenvitium    und ¶ wie    das    heutige"
    right = "zeigt, auch     ein    Mitralklappenvitium"

    # not found => no suggestion
    acro = "ZAVK"
    left = "NYHA II Niereninsuffizienz Stadium III und"
    right = "III mit zunehmender Leistungsminderung"



    # found "Zack Spiegel im Preisvergleich bei idealo.de Kosmetikspiegel"
    acro = "ZAVK"
    left = " "
    right = " "

    acro = "RÖ"
    left = "Gelenksspalt, keine Blockierungssymptomatik. ¶ "
    right = "zeigt eine Abnützung des li Kniegelenkes"

    acro = "III"
    left = "DIAGNOSEN ¶ --------- ¶¶ IÐÐ.Ð KHK"
    right = "¶ St.p. Ðfacher Stentimplantation RCA u. LAD ÐÐ,ÐÐ ¶ St.p. P"

    # found: correct!
    acro = "ZAVK"
    left = " "
    right = "Carotis"

    # not found ("Ultraschallkardiogramm" is rather uncommon)
    acro = "USKG"
    left = "ein      Aortenvitium    und ¶ wie    das    heutige"
    right = "zeigt, auch     ein    Mitralklappenvitium"

    # not found => wrong suggestion
    acro = "PAP"
    left = "einem maximalen Gradienten ¶ von ÐÐmmHg.entsprechend einem"
    right = "von rund ÐÐmmHg., kein    Pericarderguss"

    acro = "RÖ"
    left = "Gelenksspalt, keine Blockierungssymptomatik. ¶ "
    right = "zeigt eine Abnützung des li Kniegelenkes"

    acro = "KHK"
    left = "Koronarangiographie  durchgeführt.Dabei wurde eine relevante"
    right = "¶ ausgeschlossen.Eine konservative Therapie ist empfohlen."

    acro = "LKH"
    left = ""
    right = "Feldbach"

    acro = "LKH"
    left = "klin.Symptomatik ¶¶ Die Patientin wurde infolge NSTEMI vom"
    right = "Fürstenfeld "

    acro = "LKH"
    left = "klin.Symptomatik ¶¶ Die Patientin wurde infolge NSTEMI vom"
    right = "Fürstenfeld "

    acro = "LKH"
    left = "vom Notarzt in das"
    right = "überstellt wurde "

    acro = "MINS"
    left = "antigraden Fluss, leichte"
    right = "¶ und geringe TRINS, kein Pericarderguss"

    acro = "MINS"
    left = "antigraden Fluss, leichte"
    right = "¶ und geringe TRINS, kein Pericarderguss"

    acro = "AKE"
    left = "Das weitere Procedere"
    right = "oder PAVR) hängt von"

    acro = "PAP"
    left = " m / sec, keine ¶ AST.MINS Ð.Gr., TRINS"
    right = "Pericarderguss"

    acro = "NTX"
    left = "OP - Vorbereitung zur geplanten"
    right = "zur Abklärung, Angina pectoris"

    acro = "LKH"
    left = "klin.Symptomatik ¶¶ Die Patientin wurde infolge NSTEMI vom"
    right = "Fürstenfeld "

    acro = "ASS"
    left = "MEDIKATION ¶ ---------- ¶¶ Thrombo"
    right = "dant. ¶¶¶ ---------- ¶"

    acro = "AST"
    left = """ 
   uter LV ¶ Funktion und im aktuellen USKG nur leicht gardiger

    """
    right = """
    ist der Patient ¶ in seiner Belastbarkeit signifikant einges

    """

    acro = "BMS"
    left = """ 
    e ¶¶ LAD ÐÐ %, CX ÐÐ %, OM ÐÐ %: Ð BMS Stent und OM ÐÐ %: Ð



     """
    right = """
     Stents. ¶¶¶ ---------- ¶ MEDIKATION ¶ ---------- ¶¶ Plavi



     """

    acro = "CHE"
    left = """ 
    ÐÐ.Ð Hypothyreose ¶ GÐÐ.Ð Essentieller Tremor ¶ KÐÐ.Ð St. p.




     """
    right = """
     ¶ KÐÐ.Ð Kolondivertikulitis ¶ MÐÐ.ÐÐ St. p. Ovarektomie li. 




     """

    acro = "AP"  # "Angina pectoris"  - OK
    left = """ 
    e des Pat. erfolgte zur Koronarangiographie bei ¶ instabiler
    """
    right = """
    (zunehmende AP-Symptomatik bei Belastung seit Ð Monaten). ¶ 

    """

    acro = "AP"
    left = """ 
      ¶ * Labor ¶¶ patholog.: Harnsäure Ð,Ð, ges. Bilirubin Ð,ÐÐ,
     """
    right = """
     ÐÐÐ, GGT ÐÐÐ, NT- ¶ proBNP ÐÐÐ (besser im Vergleich zur letz
     """

    acro = "LV"  # "Linker Vorhof" und "linker Ventrikel" gleich!
    left = """ 
        ter), ¶ li. Vorhof mit ÐÐ mm mittelgradig vergrößert, RA und

       """
    right = """
       normal groß, ¶ Aortenklappensklerose ohne signifikante Steno


       """

    acro = "III"  # wrong results: "Innere Medizin", "Informationen , Hilfe"
    left = """ 
    e ¶ IDDM (Typ I seit ÐÐ Jahren) ¶ Diab. Nephropathie Stadium
     """
    right = """
     ¶ Renale Anämie ¶ Sek. HPT ¶ Persönlichkeitsstörung ¶ sek. H
     """





    r = base.get_web_dump_from_acro_with_context(
        left, acro, right, 2, 9)

    for t in r:
        s = acres.rater.rater.get_acronym_score(acro, t[1])
        if s > 0:
            print(str(t[0]) + "\t" + str(s) + "\t" + t[1])

    1 / 0

    print(base.get_best_acronym_web_resolution(left, acro, right, 3, 7))

    acro = "KHK"
    left = "de eine Koronarangiographie durchgeführt, dabei ¶ wurde eine"
    right = "ausgeschlossen und eine hypertensive Herzkrankheit ¶ festges"

    print(base.get_best_acronym_web_resolution(left, acro, right, 3, 7))

    1 / 0
    r = acres.evaluation.corpus.get_web_dump_from_acro_with_context(
        left, acro, right, 3, 6)

    for t in r:
        s = acres.rater.rater.get_acronym_score(acro, t[1])
        if s > 0:
            print(str(t[0]) + "\t" + str(s) + "\t" + t[1])

    1 / 0

print(acres.rater.rater.get_acronym_score("EKG", "Elektrocardiogramm"))

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

# r = acres.web.bing.ngrams_url_dump("https://news.google.com/?hl=de", 1, 2)
# r = acres.web.bing.ngrams_url_dump("http://www.bing.de/search?cc=de&q=%22" + query + "%22", 1, 10)
# = acres.web.bing.ngrams_url_dump("http://www.bing.de/search?cc=de&q=" + query, 1, 10)
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
