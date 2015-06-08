# -*- coding: utf-8
"""Context manager to add suggestions to exceptions."""
from didyoumean_internal import add_suggestions_to_exception


class didyoumean_contextmanager(object):
    """ Context manager to add suggestions to exceptions. """

    @staticmethod
    def __enter__():
        """ Method called when entering the context manager.
        Not relevant here (does not do anything). """
        pass

    @staticmethod
    def __exit__(type_, value, traceback):
        """ Method called when exiting the context manager.
        Add suggestions to the exception (if any). """
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
