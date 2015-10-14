# -*- coding: utf-8
"""APIs to add suggestions to exceptions."""
from didyoumean_internal import add_suggestions_to_exception
import functools
import sys


def didyoumean_decorator(func):
    """Decorator to add suggestions to exceptions.

    To use it, decorate one of the functions called, for instance 'main()':
    @didyoumean_decorator
    def main():
        some_code
    """
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        """Function returned by the decorator."""
        try:
            return func(*args, **kwargs)
        except:
            type_, value, traceback = sys.exc_info()
            add_suggestions_to_exception(type_, value, traceback)
            raise
    return decorated


def didyoumean_postmortem():
    """Post postem function to add suggestions to last exception thrown.

    Add suggestions to last exception thrown (in interactive mode) and
    return it (which should print it).
    """
    if hasattr(sys, 'last_type'):
        typ, val, trace = sys.last_type, sys.last_value, sys.last_traceback
        add_suggestions_to_exception(typ, val, trace)
        return val
    return None


class didyoumean_contextmanager(object):
    """Context manager to add suggestions to exceptions.

    To use it, create a context:
    with didyoumean_contextmanager():
        some_code.
    """

    def __enter__(self):
        """Method called when entering the context manager.

        Not relevant here (does not do anything).
        """
        pass

    def __exit__(self, type_, value, traceback):
        """Method called when exiting the context manager.

        Add suggestions to the exception (if any).
        """
        assert (type_ is None) == (value is None)
        if value is not None:
            if isinstance(value, type_):
                # Error is not re-raised as it is the caller's responsability
                # but the error is enhanced nonetheless
                add_suggestions_to_exception(type_, value, traceback)
            else:
                # Python 2.6 bug : http://bugs.python.org/issue7853
                # Instead of having the exception, we have its representation
                # We can try to rebuild the exception, add suggestions to it
                # and re-raise it (re-raise shouldn't be done normally but it
                # is a dirty work-around for a dirty issue).
                if isinstance(value, str):
                    value = type_(value)
                else:
                    value = type_(*value)
                add_suggestions_to_exception(type_, value, traceback)
                raise value


def didyoumean_hook(type_, value, traceback, prev_hook=sys.excepthook):
    """Hook to be substituted to sys.excepthook to enhance exceptions."""
    add_suggestions_to_exception(type_, value, traceback)
    return prev_hook(type_, value, traceback)


def didyoumean_custom_exc(shell, etype, evalue, tb, tb_offset=None):
    """Custom exception handler to replace the iPython one."""
    add_suggestions_to_exception(etype, evalue, tb)
    return shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)


def set_ipython_custom_exc(func):
    """Try to set the custom exception handler for iPython."""
    # https://mail.scipy.org/pipermail/ipython-dev/2012-April/008945.html
    # http://stackoverflow.com/questions/1261668/cannot-override-sys-excepthook
    try:
        get_ipython().set_custom_exc((Exception,), func)
    except NameError:
        pass  # get_ipython does not exist - ignore


def didyoumean_enablehook():
    """Function to set hooks to their custom value."""
    sys.excepthook = didyoumean_hook
    set_ipython_custom_exc(didyoumean_custom_exc)


def didyoumean_disablehook():
    """Function to set hooks to their normal value."""
    sys.excepthook = sys.__excepthook__
    set_ipython_custom_exc(None)

# NOTE: It could be funny to have a magic command in Python
# https://ipython.org/ipython-doc/dev/config/custommagics.html
