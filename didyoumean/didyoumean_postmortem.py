# -*- coding: utf-8
"""Post-mortem to add suggestions to exceptions."""
from didyoumean_internal import add_suggestions_to_exception
import sys


def didyoumean_postmortem():
    """Post postem function to add suggestions to last exception thrown
    (in interactive mode) and return it (which should print it)."""
    if hasattr(sys, 'last_type'):
        typ, val, trace = sys.last_type, sys.last_value, sys.last_traceback
        add_suggestions_to_exception(typ, val, trace)
        return val
    return None
