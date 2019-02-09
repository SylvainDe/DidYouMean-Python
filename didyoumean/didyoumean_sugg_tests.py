# -*- coding: utf-8
"""Unit tests for get_suggestions_for_exception."""
import unittest

DESCRIPT_REQUIRES_TYPE_RE = r"descriptor '\w+' requires a 'set' object but received a 'int'"

class SetAddIntRegexpTests(unittest.TestCase):

    def test_try_except_as_e(self):
        try:
            set.add(0)
        except TypeError as e:
            msg = next((a for a in e.args if isinstance(a, str)), '')
            self.assertRegexpMatches(msg, DESCRIPT_REQUIRES_TYPE_RE)
            self.assertRegexpMatches(str(e), DESCRIPT_REQUIRES_TYPE_RE)
            self.assertRegexpMatches(repr(e), DESCRIPT_REQUIRES_TYPE_RE)

    def test_assertRaisesRegex(self):
        self.assertRaisesRegex(TypeError, DESCRIPT_REQUIRES_TYPE_RE, set.add, 0)

    def test_assertRaisesRegex_contextman(self):
        with self.assertRaisesRegex(TypeError, DESCRIPT_REQUIRES_TYPE_RE):
            set.add(0)

if __name__ == '__main__':
    unittest.main()
