# -*- coding: utf-8
"""Decorator to add suggestions to exceptions."""
from didyoumean import add_suggestions_to_exception
import functools
import sys

def didyoumean(func):
    """Decorator to add a suggestions to error messages."""
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            type, value, traceback = sys.exc_info()
            add_suggestions_to_exception(type, value, traceback)
            raise
    return decorated

