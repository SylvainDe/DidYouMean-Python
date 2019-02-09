# -*- coding: utf-8
"""Unit tests for get_suggestions_for_exception."""
import unittest2
import sys


def get_exception(code):
    """Helper function to run code and get what it throws (or None)."""
    try:
        exec(code)
    except:
        return sys.exc_info()
    return None


TYPE_NAME = r"[\w\.-]+"
DESCRIPT_REQUIRES_TYPE_RE = r"^descriptor '(\w+)' requires a '({0})' " \
        r"object but received a '({0})'$".format(TYPE_NAME)


class GetSuggestionsTests(unittest2.TestCase):

    def throws(self, code, error_type, error_msg):
        details = "Running following code :\n---\n{0}\n---".format(code)
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

    def test_toto(self):
        bad_code = 'set.add(0)'
        self.throws(bad_code, TypeError, DESCRIPT_REQUIRES_TYPE_RE)

    def test_tutu(self):
        pass  # set.add(0)

    def test_titi(self):
        self.assertRaisesRegex(TypeError, DESCRIPT_REQUIRES_TYPE_RE, set.add, 0)

    def test_tata(self):
        with self.assertRaisesRegex(TypeError, DESCRIPT_REQUIRES_TYPE_RE):
            set.add(0)

if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
