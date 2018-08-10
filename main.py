import acres.util.text
from acres.benchmark import fix_line_endings
from acres.util import functions

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
    text = functions.reduce_repeated_chars(text, " ", 1)
    text = text.replace(break_marker + " " + break_marker, break_marker + break_marker)
    text = text.replace(break_marker + " " + break_marker, break_marker + break_marker)
    text = functions.reduce_repeated_chars(text, break_marker, 2)

    print(text)
    print(text.replace(break_marker, break_marker + "\n"))

    1 / 0

    fix_line_endings.test_fine_ending_fixings()
