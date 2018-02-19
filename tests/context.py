import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from acres import create_dumps
from acres import text_cleanser
from acres import find_synonym_for_acronyms_in_ngrams
from acres import functions
from acres import get_acronyms_from_web
from acres import get_synonyms_from_ngrams
from acres import rate_acronym_resolutions
