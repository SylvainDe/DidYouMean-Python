# -*- coding: utf-8
"""Hook on sys.excepthoob to add suggestions to exceptions."""
from didyoumean import add_suggestions_to_exception
import sys


def didyoumean_hook(type, value, traceback, prev_hook=sys.excepthook):
    """Hook to be substituted to sys.excepthook to enhance exceptions."""
    add_suggestions_to_exception(type, value, traceback)
    return prev_hook(type, value, traceback)

sys.excepthook = didyoumean_hook
