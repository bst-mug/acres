"""
.. deprecated:: 0.1
   Use `fastngram` instead.

Package grouping modules related to the n-gram expansion strategy as originally implemented by
Prof. Stefan Schulz. Since this implementation relies on regular expressions, it typically runs
slower than `fastngram`.
"""
from acres.ngram import finder, ngrams

__all__ = ['finder', 'ngrams']
