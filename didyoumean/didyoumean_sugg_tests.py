# -*- coding: utf-8
"""Unit tests for get_suggestions_for_exception."""
from didyoumean_internal import (
    get_suggestions_for_exception,
    AVOID_REC_MSG,
)
import didyoumean_common_tests
import didyoumean_re
import sys


unittest_module = didyoumean_common_tests.unittest_module

# Variable to hold info about the exceptions caught
# (to print them for instance).
# It is not used when set to None. It can be set to
# something else when the file is run on its own.
exc_history = None

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
    """Generic class to test get_suggestions_for_exception.

    Many tests do not correspond to any handled exceptions but are
    kept because it is quite convenient to have a large panel of examples.
    Also, some correspond to example where suggestions could be added, those
    are flagged with a NICE_TO_HAVE comment.
    Finally, whenever it is easily possible, the code with the suggestions
    taken into account is usually tested too to ensure that the suggestion does
    work.
    """

    def throws(
        self, code, error_info, sugg=None, version_range=None, interpreters=None
    ):
        """Run code and check it throws and relevant suggestions are provided.

        Helper function to run code, check that it throws, what it throws and
        that the exception leads to the expected suggestions.
        version_range and interpreters can be provided if the test depends on
        the used environment.
        """
        sugg = sorted(listify(sugg, [], str))
        error_type, error_msg = error_info
        details = "Running following code :\n---\n{0}\n---".format(code)
        exc = get_exception(code)
        self.assertFalse(exc is None, "No exc thrown." + details)
        type_caught, value, traceback = exc
        suggestions = sorted(get_suggestions_for_exception(value, traceback))
        self.log_exception(code, exc, suggestions)

        self.assertTrue(isinstance(value, type_caught))
        self.assertTrue(
            issubclass(type_caught, error_type),
            "{0} ({1}) not a subclass of {2}".format(type_caught, value, error_type)
            + details,
        )
        msg = next((a for a in value.args if isinstance(a, str)), "")
        if error_msg:
            self.assertRegexp(msg, error_msg, details)
        self.assertEqual(suggestions, sugg, details)

    def log_exception(self, code, exc, suggestions):
        """Log exception for debug purposes."""
        if exc_history is not None:
            type_caught, value, traceback = exc
            is_pypy = hasattr(sys, "pypy_translation_info")
            exc_history.append(
                (
                    sys.version_info,
                    "pypy" if is_pypy else "cpython",
                    code,
                    type_caught,
                    value,
                    suggestions,
                )
            )

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
        suggs = [
            "increase the limit with `sys.setrecursionlimit(limit)`"
            " (current value is 200)",
            AVOID_REC_MSG,
        ]
        self.throws(code, (RuntimeError, didyoumean_re.MAX_RECURSION_DEPTH_RE), suggs)
        sys.setrecursionlimit(initial_recursion_limit)


if __name__ == "__main__":
    print(sys.version_info)
    exc_history = []
    main_module = sys.modules[__name__]
    loader = unittest_module.TestLoader().loadTestsFromModule(main_module)
    unittest_module.TextTestRunner().run(loader)
    print(exc_history)
