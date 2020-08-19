"""
.. deprecated:: 0.1
   Web-based expansion has not been used recently (e.g. not used in Michel's PhD Thesis) because it
   is not reproducible. Consider using a fixed corpus instead or an ensemble model with a fixed
   sense inventory.

Package grouping modules related to the web expansion strategy. It contains two implementations of
web-based resolution, namely based on the Azure API (`azure`) and on parsing Bing's SERP (`bing`).
"""
from acres.web import azure, base, bing

__all__ = ['azure', 'base', 'bing']
