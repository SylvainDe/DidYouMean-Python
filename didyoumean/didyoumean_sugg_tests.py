# -*- coding: utf-8
"""Unit tests for get_suggestions_for_exception."""
import unittest2
import sys

DESCRIPT_REQUIRES_TYPE_RE = r"descriptor '\w+' requires a 'set' object but received a 'int'"

class SetAddIntRegexpTests(unittest2.TestCase):

    def throws(self, code, error_type, error_msg):
        details = "Running following code :\n---\n{0}\n---".format(code)
        try:
            exec(code)
        except:
            type_caught, e, traceback = sys.exc_info()
        else:
            self.assertFalse(True, "No exc thrown." + details)
        self.assertTrue(isinstance(e, type_caught))
        self.assertTrue(issubclass(type_caught, error_type),
            "{0} ({1}) not a subclass of {2}".format(type_caught, e, error_type) + details)
        msg = next((a for a in e.args if isinstance(a, str)), '')
        self.assertRegexpMatches(msg, error_msg, details)
        self.assertRegexpMatches(str(e), error_msg, details)
        self.assertRegexpMatches(repr(e), error_msg, details)

    def test_toto(self):
        self.throws('set.add(0)', TypeError, DESCRIPT_REQUIRES_TYPE_RE)

    def test_tutu(self):
        try:
            set.add(0)
        except TypeError as e:
            msg = next((a for a in e.args if isinstance(a, str)), '')
            self.assertRegexpMatches(msg, DESCRIPT_REQUIRES_TYPE_RE)
            self.assertRegexpMatches(str(e), DESCRIPT_REQUIRES_TYPE_RE)
            self.assertRegexpMatches(repr(e), DESCRIPT_REQUIRES_TYPE_RE)

    def test_tete(self):
        try:
            set.add(0)
        except:
            type_caught, e, traceback = sys.exc_info()
            msg = next((a for a in e.args if isinstance(a, str)), '')
            self.assertRegexpMatches(msg, DESCRIPT_REQUIRES_TYPE_RE)
            self.assertRegexpMatches(str(e), DESCRIPT_REQUIRES_TYPE_RE)
            self.assertRegexpMatches(repr(e), DESCRIPT_REQUIRES_TYPE_RE)
        else:
            self.assertFalse(True)

    def test_titi(self):
        self.assertRaisesRegex(TypeError, DESCRIPT_REQUIRES_TYPE_RE, set.add, 0)

    def test_tata(self):
        with self.assertRaisesRegex(TypeError, DESCRIPT_REQUIRES_TYPE_RE):
            set.add(0)

    def test_tyty(self):
        f = set.add
        with self.assertRaisesRegex(TypeError, DESCRIPT_REQUIRES_TYPE_RE):
            f(0)


if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
