# -*- coding: utf-8
"""Unit tests for get_suggestions_for_exception."""
from didyoumean_internal import get_suggestions_for_exception, \
    STAND_MODULES, AVOID_REC_MSG, \
    APPLY_REMOVED_MSG, BUFFER_REMOVED_MSG, CMP_REMOVED_MSG, \
    CMP_ARG_REMOVED_MSG, \
    MEMVIEW_ADDED_MSG, RELOAD_REMOVED_MSG, STDERR_REMOVED_MSG
import didyoumean_common_tests as common
import unittest2
import didyoumean_re as re
import warnings
import sys
import math
import os
import tempfile
from shutil import rmtree


this_is_a_global_list = []  # Value does not really matter but the type does


def func_gen(name='some_func', param='', body='pass', args=None):
    """Generate code corresponding to a function definition.

    Generate code for function definition (and eventually a call to it).
    Parameters are : name (with default), body (with default),
    parameters (with default) and arguments to call the functions with (if not
    provided or provided None, function call is not included in generated
    code).
    """
    func = "def {0}({1}):\n\t{2}\n".format(name, param, body)
    call = "" if args is None else "{0}({1})\n".format(name, args)
    return func + call


def my_generator():
    """Generate values for testing purposes.

    my_generator
    This is my generator, baby.
    """
    for i in range(5):
        yield i


def endlessly_recursive_func(n):
    """Call itself recursively with no end."""
    # http://stackoverflow.com/questions/871887/using-exec-with-recursive-functions
    return endlessly_recursive_func(n-1)


class FoobarClass():
    """Dummy class for testing purposes."""

    def __init__(self):
        """Constructor."""
        self.babar = 2

    @classmethod
    def this_is_cls_mthd(cls):
        """Just a class method."""
        return 5

    def nameerror_self(self):
        """Should be self.babar."""
        return babar

    def nameerror_self2(self):
        """Should be self.this_is_cls_mthd (or FoobarClass)."""
        return this_is_cls_mthd

    @classmethod
    def nameerror_cls(cls):
        """Should be cls.this_is_cls_mthd (or FoobarClass)."""
        return this_is_cls_mthd

    def some_method(self):
        """Method for testing purposes."""
        pass

    def some_method2(self, x):
        """Method for testing purposes."""
        pass

    def _some_semi_private_method(self):
        """Method for testing purposes."""
        pass

    def __some_private_method(self):
        """Method for testing purposes."""
        pass

    def some_method_missing_self_arg():
        """Method for testing purposes."""
        pass

    def some_method_missing_self_arg2(x):
        """Method for testing purposes."""
        pass

    @classmethod
    def some_cls_method_missing_cls():
        """Class method for testing purposes."""
        pass

    @classmethod
    def some_cls_method_missing_cls2(x):
        """Class method for testing purposes."""
        pass


# Logic to be able to have different tests on various version of Python
FIRST_VERSION = (0, 0)
LAST_VERSION = (10, 0)
ALL_VERSIONS = (FIRST_VERSION, LAST_VERSION)
INTERPRETERS = ['cython', 'pypy']


def from_version(version):
    """Create tuple describing a range of versions from a given version."""
    return (version, LAST_VERSION)


def up_to_version(version):
    """Create tuple describing a range of versions up to a given version."""
    return (FIRST_VERSION, version)


def version_in_range(version_range):
    """Test if current version is in a range version."""
    beg, end = version_range
    return beg <= sys.version_info < end


def interpreter_in(interpreters):
    """Test if current interpreter is in a list of interpreters."""
    is_pypy = hasattr(sys, "pypy_translation_info")
    interpreter = 'pypy' if is_pypy else 'cython'
    return interpreter in interpreters


def format_str(template, *args):
    """Format multiple string by using first arg as a template."""
    return [template.format(arg) for arg in args]


def listify(value, default):
    """Return list from value, using default value if value is None."""
    if value is None:
        value = default
    if not isinstance(value, list):
        value = [value]
    if default:
        assert all(v in default for v in value)
    return value


def no_exception(code):
    """Helper function to run code and check it works."""
    exec(code)


def get_exception(code):
    """Helper function to run code and get what it throws."""
    try:
        no_exception(code)
    except:
        return sys.exc_info()
    assert False, "No exception thrown running\n---\n{0}\n---".format(code)


# UnboundLocalError for UnboundLocalErrorTests
UNBOUNDLOCAL = (UnboundLocalError, re.VARREFBEFOREASSIGN_RE)
UNKNOWN_UNBOUNDLOCAL = (UnboundLocalError, None)


class GetSuggestionsTests(unittest2.TestCase):
    """Generic class to test get_suggestions_for_exception.

    Many tests do not correspond to any handled exceptions but are
    kept because it is quite convenient to have a large panel of examples.
    Also, some correspond to example where suggestions could be added, those
    are flagged with a NICE_TO_HAVE comment.
    Finally, whenever it is easily possible, the code with the suggestions
    taken into account is usually tested too to ensure that the suggestion does
    work.
    """

    def runs(self, code, version_range=None, interpreters=None):
        """Helper function to run code.

        version_range and interpreters can be provided if the test depends on
        the used environment.
        """
        interpreters = listify(interpreters, INTERPRETERS)
        if version_range is None:
            version_range = ALL_VERSIONS
        if version_in_range(version_range) and interpreter_in(interpreters):
            no_exception(code)

    def throws(self, code, error_info,
               sugg=None, version_range=None, interpreters=None):
        """Run code and check it throws and relevant suggestions are provided.

        Helper function to run code, check that it throws, what it throws and
        that the exception leads to the expected suggestions.
        version_range and interpreters can be provided if the test depends on
        the used environment.
        """
        if version_range is None:
            version_range = ALL_VERSIONS
        interpreters = listify(interpreters, INTERPRETERS)
        sugg = sorted(listify(sugg, []))
        if version_in_range(version_range) and interpreter_in(interpreters):
            error_type, error_msg = error_info
            type_caught, value, traceback = get_exception(code)
            details = "Running following code :\n---\n{0}\n---".format(code)
            self.assertTrue(isinstance(value, type_caught))
            self.assertTrue(
                issubclass(type_caught, error_type),
                "{0} ({1}) not a subclass of {2}"
                .format(type_caught, value, error_type) + details)
            msg = next((a for a in value.args if isinstance(a, str)), '')
            if error_msg is not None:
                self.assertRegexpMatches(msg, error_msg)
            suggestions = sorted(
                get_suggestions_for_exception(value, traceback))
            self.assertEqual(suggestions, sugg, details)


class UnboundLocalErrorTests(GetSuggestionsTests):
    """Class for tests related to UnboundLocalError."""

    def test_unbound_typo(self):
        """Should be foo."""
        code = 'def func():\n\tfoo = 1\n\t{0} +=1\nfunc()'
        typo, sugg = "foob", "foo"
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, UNBOUNDLOCAL, "'" + sugg + "' (local)")
        self.runs(good_code)

    def test_unbound_global(self):
        """Should be global nb."""
        # NICE_TO_HAVE
        code = 'nb = 0\ndef func():\n\t{0}\n\tnb +=1\nfunc()'
        sugg = 'global nb'
        bad_code, good_code = format_str(code, "", sugg)
        self.throws(bad_code, UNBOUNDLOCAL)
        self.runs(good_code)  # this is to be run afterward :-/

    def test_unbound_nonlocal(self):
        """Shoud be nonlocal nb."""
        # NICE_TO_HAVE
        code = 'def foo():\n\tnb = 0\n\tdef bar():' \
               '\n\t\t{0}\n\t\tnb +=1\n\tbar()\nfoo()'
        sugg = 'nonlocal nb'
        bad_code, good_code = format_str(code, "", sugg)
        self.throws(bad_code, UNBOUNDLOCAL)
        version = (3, 0)
        self.runs(good_code, from_version(version))
        self.throws(good_code, INVALIDSYNTAX, [], up_to_version(version))

    def test_unbound_nonlocal_and_global(self):
        """Shoud be nonlocal nb or global."""
        # NICE_TO_HAVE
        code = 'nb = 1\ndef foo():\n\tnb = 0\n\tdef bar():' \
               '\n\t\t{0}\n\t\tnb +=1\n\tbar()\nfoo()'
        sugg1, sugg2 = 'nonlocal nb', 'global nb'
        bad_code, good_code1, good_code2 = format_str(code, "", sugg1, sugg2)
        self.throws(bad_code, UNBOUNDLOCAL)
        self.runs(good_code2)
        version = (3, 0)
        self.runs(good_code1, from_version(version))
        self.throws(good_code1, INVALIDSYNTAX, [], up_to_version(version))

    def test_unmatched_msg(self):
        """Test that arbitrary strings are supported."""
        self.throws(
            'raise UnboundLocalError("unmatched UNBOUNDLOCAL")',
            UNKNOWN_UNBOUNDLOCAL)


if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
