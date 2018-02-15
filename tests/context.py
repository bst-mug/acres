import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from acres import create_acro_dump
from acres import CreateMorphoDump
from acres import CreateNgramDumps
from acres import ExpansionOfAcronyms
from acres import Filters
from acres import FindSynonymForAcronymsInNgrams
from acres import Functions
from acres import GetAcronymsFromWeb
from acres import GetSynonymsFromNgrams
from acres import ling
from acres import RateAcronymResolutions