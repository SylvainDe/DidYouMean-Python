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


def listify(value, default, expected_types):
    """Return list from value, using default value if value is None."""
    if value is None:
        value = list(default)
    if not isinstance(value, list):
        value = [value]
    if default:
        assert all(v in default for v in value), "%s %s" % (value, default)
    if expected_types is not None:
        assert all(isinstance(v, expected_types) for v in value), "%s %s" % (
            value,
            expected_types,
        )
    return value


def get_exception(code):
    """Helper function to run code and get what it throws (or None)."""
    try:
        exec(code)
    except:
        return sys.exc_info()
    return None


class GetSuggestionsTests(unittest_module.TestCase):
    """Generic class to test things."""

    def throws(self, code, error_type, error_msg):
        """Run code and check it throws."""
        details = "Running following code :\n---\n{0}\n---".format(code)

        exc = get_exception(code)

        self.assertFalse(exc is None, "No exc thrown." + details)
        type_caught, value, traceback = exc

        self.assertTrue(isinstance(value, type_caught))
        self.assertTrue(
            issubclass(type_caught, error_type),
            "{0} ({1}) not a subclass of {2}".format(type_caught, value, error_type)
            + details,
        )

        msg = next((a for a in value.args if isinstance(a, str)), "")
        self.assertRegexp(msg, error_msg, details)

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
        code = "endlessly_recursive_func(0)"
        max_recur_regexp = r"^maximum recursion depth exceeded$"
        self.throws(code, RuntimeError, max_recur_regexp)
        sys.setrecursionlimit(initial_recursion_limit)


if __name__ == "__main__":
    main_module = sys.modules[__name__]
    loader = unittest_module.TestLoader().loadTestsFromModule(main_module)
    unittest_module.TextTestRunner().run(loader)
