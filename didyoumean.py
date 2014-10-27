# -*- coding: utf-8
"""Decorator to have suggestions when variable/functions do not exist."""
import inspect
import functools
import difflib
import builtins


def get_var_suggestions(var, inspect_frame, lim=10, cutoff=0.6):
    """Get the lim suggestions closest to the variable names."""
    return difflib.get_close_matches(
        var,
        list(inspect_frame.f_locals.keys()) +
        list(inspect_frame.f_globals.keys()) +
        list(inspect_frame.f_builtins.keys()),
        lim,
        cutoff)


def get_method_suggestions(type_, method, lim=10, cutoff=0.6):
    """Get the lim suggestions closest to the variable names."""
    if method in dir(builtins):
        return [method + '(' + type_ + ')']
    # todo : add hardcoded logic for usual containers : add, append, etc
    return difflib.get_close_matches(
        method,
        dir(type_),
        lim,
        cutoff)


def get_var_name_from_nameerror(exc):
    """Extract the variable name from NameError."""
    assert isinstance(exc, NameError)
    return exc.args[0].split("'")[1]


def get_type_and_method_from_attributeerror(exc):
    """Extract the type and the method name from AttributeError."""
    assert isinstance(exc, AttributeError)
    split = exc.args[0].split("'")
    return (split[1], split[3])


def didyoumean(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NameError as exc:
            assert len(exc.args) == 1
            exc.args = (exc.args[0] + ". Did you mean " + ', '.join(
                get_var_suggestions(
                    get_var_name_from_nameerror(exc),
                    inspect.trace()[-1][0])), )
            raise
        except AttributeError as exc:
            assert len(exc.args) == 1
            type_, method = get_type_and_method_from_attributeerror(exc)
            exc.args = (exc.args[0] + ". Did you mean " + ', '.join(
                get_method_suggestions(type_, method)), )
            raise
        # Could be added : IndexError, KeyError
    return decorated
