# -*- coding: utf-8
"""Hook on sys.excepthook to add suggestions to exceptions."""
from didyoumean import add_suggestions_to_exception
import sys


def didyoumean_hook(type_, value, traceback, prev_hook=sys.excepthook):
    """Hook to be substituted to sys.excepthook to enhance exceptions."""
    add_suggestions_to_exception(type_, value, traceback)
    return prev_hook(type_, value, traceback)

sys.excepthook = didyoumean_hook
