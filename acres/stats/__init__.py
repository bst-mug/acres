"""
Package with modules to collect statistics from the gold-standard (`senses`), the training corpus
(`stats`), and a fixed sense inventory (`dictionary`).
"""
from acres.stats import dictionary, senses, stats

__all__ = ['dictionary', 'senses', 'stats']
