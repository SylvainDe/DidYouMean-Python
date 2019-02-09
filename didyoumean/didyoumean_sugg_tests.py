# -*- coding: utf-8
"""Unit tests for get_suggestions_for_exception."""
import unittest2
import sys



# Logic to be able to have different tests on various version of Python
FIRST_VERSION = (0, 0)
LAST_VERSION = (10, 0)
ALL_VERSIONS = (FIRST_VERSION, LAST_VERSION)
INTERPRETERS = ['cpython', 'pypy']


def version_in_range(version_range):
    """Test if current version is in a range version."""
    beg, end = version_range
    return beg <= sys.version_info < end


def interpreter_in(interpreters):
    """Test if current interpreter is in a list of interpreters."""
    is_pypy = hasattr(sys, "pypy_translation_info")
    interpreter = 'pypy' if is_pypy else 'cpython'
    return interpreter in interpreters


class PythonEnvRange(object):
    """Class to describe a (range of) Python environment.

    A range of Python environments consist of:
     - a range of Python version (tuple)
     - a list of interpreters (strings).
    """

    def __init__(self, version_range=None, interpreters=None):
        """Init a PythonEnvRange.

        The parameters are:
         - a range of version (optional - ALL if not provided)
         - a list of interpreters (optional - ALL if not provided).
            Also, a single interpreter can be provided.
        """
        self.interpreters = listify(interpreters, INTERPRETERS, str)
        self.version_range = \
            ALL_VERSIONS if version_range is None else version_range

    def contains_current_env(self):
        """Check if current environment is in PythonEnvRange object."""
        return version_in_range(self.version_range) and \
            interpreter_in(self.interpreters)


def listify(value, default, expected_types):
    """Return list from value, using default value if value is None."""
    if value is None:
        value = list(default)
    if not isinstance(value, list):
        value = [value]
    if default:
        assert all(v in default for v in value), "%s %s" % (value, default)
    if expected_types is not None:
        assert all(isinstance(v, expected_types) for v in value), \
            "%s %s" % (value, expected_types)
    return value


def get_exception(code):
    """Helper function to run code and get what it throws (or None)."""
    try:
        exec(code)
    except:
        return sys.exc_info()
    return None




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

    def throws(self, code, error_info,
               sugg=None, version_range=None, interpreters=None):
        """Run code and check it throws and relevant suggestions are provided.

        Helper function to run code, check that it throws, what it throws and
        that the exception leads to the expected suggestions.
        version_range and interpreters can be provided if the test depends on
        the used environment.
        """
        sugg = sorted(listify(sugg, [], str))
        error_type, error_msg = error_info
        details = "Running following code :\n---\n{0}\n---".format(code)
        if PythonEnvRange(version_range, interpreters).contains_current_env():
            exc = get_exception(code)
            self.assertFalse(exc is None, "No exc thrown." + details)
            type_caught, value, traceback = exc
            self.assertTrue(isinstance(value, type_caught))
            self.assertTrue(
                issubclass(type_caught, error_type),
                "{0} ({1}) not a subclass of {2}"
                .format(type_caught, value, error_type) + details)
            msg = next((a for a in value.args if isinstance(a, str)), '')
            if error_msg is not None:
                self.assertRegexpMatches(msg, error_msg, details)
            # suggestions = sorted(
            #     get_suggestions_for_exception(value, traceback))
            # self.assertEqual(suggestions, sugg, details)


class TypeErrorTests(GetSuggestionsTests):
    """Class for tests related to TypeError."""

    def test_toto(self):
        bad_code = 'set.add(0)'
        TYPE_NAME = r"[\w\.-]+"
        DESCRIPT_REQUIRES_TYPE_RE = r"^descriptor '(\w+)' requires a '({0})' " \
                r"object but received a '({0})'$".format(TYPE_NAME)
        DESCREXPECT = (TypeError, DESCRIPT_REQUIRES_TYPE_RE)
        self.throws(bad_code, DESCREXPECT, interpreters='cpython')

    def test_tutu(self):
        pass  # set.add(0)


if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
