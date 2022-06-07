# -*- coding: utf-8
"""Unit tests for get_suggestions_for_exception."""
import sys

try:
    import unittest2

    unittest_module = unittest2
except ImportError:
    import unittest

    unittest_module = unittest
except AttributeError:
    import unittest

    unittest_module = unittest


initial_recursion_limit = sys.getrecursionlimit()


def endlessly_recursive_func(n):
    """Call itself recursively with no end."""
    # http://stackoverflow.com/questions/871887/using-exec-with-recursive-functions
    return endlessly_recursive_func(n - 1)


def get_exception(code):
    """Helper function to run code and get what it throws (or None)."""
    try:
        code(0)
    except:
        return sys.exc_info()
    return None


class GetSuggestionsTests(unittest_module.TestCase):
    """Generic class to test things."""

    def throws(self, code, error_msg):
        """Run code and check it throws."""
        _, value, _ = get_exception(code)
        msg = next((a for a in value.args if isinstance(a, str)), "")
        self.assertRegexp(msg, error_msg)

    def assertRegexp(self, text, regex, msg=None):
        """Wrapper around the different names for assertRegexp...."""
        for name in ["assertRegex", "assertRegexpMatches"]:
            if hasattr(self, name):
                return getattr(self, name)(text, regex, msg)
        self.assertTrue(False, "No method to check assertRegexp")


class RuntimeErrorTests(GetSuggestionsTests):
    """Class for tests related to RuntimeError."""

    def test_max_depth(self):
        """Reach maximum recursion depth."""
        sys.setrecursionlimit(200)
        self.throws(endlessly_recursive_func, r"^maximum recursion depth exceeded$")
        sys.setrecursionlimit(initial_recursion_limit)


if __name__ == "__main__":
    main_module = sys.modules[__name__]
    loader = unittest_module.TestLoader().loadTestsFromModule(main_module)
    unittest_module.TextTestRunner().run(loader)
