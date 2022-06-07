# -*- coding: utf-8
"""Unit tests for regexps from didyoumean_re.py."""
import didyoumean_re as re
import sys
from didyoumean_common_tests import unittest_module

NO_GROUP = ((), dict())
# Various technical flags to check more that meet the eyes in tests
# Flag used to check that a text only matches the expected regexp and not
# the other to ensure we do not have ambiguous/double regexp matching.
CHECK_OTHERS_DONT_MATCH = True
# Flag to check that the regexp provided does correspond to a regexp
# listed in re.ALL_REGEXPS
CHECK_RE_LISTED = True
# Flag to check that the name used for the regexp in re.ALL_REGEXPS
# does match the naming convention
CHECK_RE_NAME = True
# Flag to check that the regex does match a few conventions such as:
# starts with ^, ends with $.
CHECK_RE_VALUE = True


class RegexTests(unittest_module.TestCase):
    """Tests to check that error messages match the regexps."""

    def assertRegexp(self, text, regex, msg=None):
        """Wrapper around the different names for assertRegexp...."""
        for name in ["assertRegex", "assertRegexpMatches"]:
            if hasattr(self, name):
                return getattr(self, name)(text, regex, msg)
        self.assertTrue(False, "No method to check assertRegexp")

    def assertNotRegexp(self, text, regex, msg=None):
        """Wrapper around the different names for assertRegexpNot...."""
        for name in ["assertNotRegex", "assertNotRegexpMatches"]:
            if hasattr(self, name):
                return getattr(self, name)(text, regex, msg)
        self.assertTrue(False, "No method to check assertNotRegexp")

    def re_matches(self, text, regexp, results):
        """Check that text matches regexp and gives the right match groups.

        result is a tuple containing the expected return values for groups()
        and groupdict().
        """
        groups, named_groups = results
        self.assertRegexp(text, regexp)  # does pretty printing
        match = re.match(regexp, text)
        self.assertTrue(match)
        self.assertEqual(groups, match.groups())
        self.assertEqual(named_groups, match.groupdict())
        self.check_more_about_re(text, regexp)

    def check_more_about_re(self, text, regexp):
        """Check various properties about the regexp.

        Properties checked are configurable via global constants. These
        properties are not stricly speaking required but they help to
        detect potential issues much more quickly.
        """
        if CHECK_RE_VALUE:
            self.assertTrue(regexp.startswith("^"))
            self.assertTrue(regexp.endswith("$"))
        found = False
        for other_name, other_re in re.ALL_REGEXPS.items():
            if other_re == regexp:
                found = True
                if CHECK_RE_NAME:
                    self.assertTrue(other_name.endswith("_RE"))
            elif CHECK_OTHERS_DONT_MATCH:
                details = "text '%s' matches %s (on top of %s)" % (
                    text,
                    other_name,
                    regexp,
                )
                self.assertNotRegexp(text, other_re, details)
                no_match = re.match(other_re, text)
                self.assertEqual(no_match, None, details)
        if CHECK_RE_LISTED:
            self.assertTrue(found)

    def test_max_recursion_depth(self):
        """Test MAX_RECURSION_DEPTH_RE."""
        msg = "maximum recursion depth exceeded"
        self.re_matches(msg, re.MAX_RECURSION_DEPTH_RE, NO_GROUP)


if __name__ == "__main__":
    print(sys.version_info)
    unittest_module.main()
