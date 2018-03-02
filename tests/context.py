import os
import sys

# sys.path.insert(0, os.path.abspath(
#     os.path.join(os.path.dirname(__file__), '..')))

from acres import create_dumps
from acres import find_synonym_for_acronyms_in_ngrams
from acres import functions
from acres import get_web_ngram_stat
from acres import get_synonyms_from_ngrams
from acres import rate_acronym_resolutions
from acres import text_cleanser
