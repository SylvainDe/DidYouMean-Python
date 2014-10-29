# -*- coding: utf-8
"""Decorator to have suggestions when variable/functions do not exist."""
import functools
import difflib
import builtins
import sys

#: Standard modules we'll consider while searching for undefined values - to be completed
STAND_MODULES = set(['string', 'os', 'sys', 're', 'math', 'random', 'datetime', 'timeit', 'unittest', 'itertools', 'functools'])


def get_var_suggestions(var, frame, lim=10, cutoff=0.6):
    """Get the lim suggestions closest to the variable names."""
    sugg = []
    local_var = frame.f_locals
    for spec_var in ('self', 'cls'):
        if hasattr(local_var.get(spec_var, None), var):
            sugg.append(spec_var + '.' + var)
    if var in STAND_MODULES:
        sugg.append('import ' + var)
    sugg.extend(difflib.get_close_matches(
        var,
        list(local_var.keys()) +
        list(frame.f_globals.keys()) +
        list(frame.f_builtins.keys()),
        lim,
        cutoff))
    return sugg


def get_method_suggestions(type_, method, lim=10, cutoff=0.6):
    """Get the lim suggestions closest to the method name for a given type."""
    sugg = []
    if method in dir(builtins):
        sugg.append(method + '(' + type_ + ')')
    # todo : add hardcoded logic for usual containers : add, append, etc
    sugg.extend(difflib.get_close_matches(
        method,
        dir(eval(type_)),  # todo: this can and should be changed
        lim,
        cutoff))
    return sugg


def get_var_name_from_nameerror(exc):
    """Extract the variable name from NameError."""
    assert isinstance(exc, NameError)
    return exc.args[0].split("'")[1]


def get_type_and_method_from_attributeerror(exc):
    """Extract the type and the method name from AttributeError."""
    assert isinstance(exc, AttributeError)
    split = exc.args[0].split("'")
    return (split[1], split[3])


def get_suggestion_string(sugg):
    """Return the suggestion list as a string."""
    return ". Did you mean " + ', '.join(sugg) if sugg else ""


def debug_traceback(traceback):
    """Print information from the traceback for debugging purposes."""
    while traceback:
        frame = traceback.tb_frame
        assert traceback.tb_lineno == frame.f_lineno
        assert traceback.tb_lasti == frame.f_lasti
        print(traceback,
              traceback.tb_lasti,
              traceback.tb_lineno,
              frame.f_code.co_name)
        traceback = traceback.tb_next


def add_suggestions_to_exception(type, value, traceback):
    """Add suggestion to an exception.
    Arguments are such as provided by sys.exc_info()."""
    # We care about the last element of the traceback
    end_traceback = traceback
    while end_traceback.tb_next:
        end_traceback = end_traceback.tb_next
    if issubclass(type, NameError):
        assert len(value.args) == 1
        var = get_var_name_from_nameerror(value)
        sugg = get_var_suggestions(var, end_traceback.tb_frame)
        value.args = (value.args[0] + get_suggestion_string(sugg), )
        assert len(value.args) == 1
    elif issubclass(type, AttributeError):
        assert len(value.args) == 1
        type_, method = get_type_and_method_from_attributeerror(value)
        sugg = get_method_suggestions(type_, method)
        value.args = (value.args[0] + get_suggestion_string(sugg), )
        assert len(value.args) == 1
    # Could be added : IndexError, KeyError


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


def didyoumean_hook(type, value, traceback, prev_hook=sys.excepthook):
    """Hook to be substituted to sys.excepthook to enhance exceptions."""
    add_suggestions_to_exception(type, value, traceback)
    return prev_hook(type, value, traceback)
# when it will work - sys.excepthook = didyoumean_hook
