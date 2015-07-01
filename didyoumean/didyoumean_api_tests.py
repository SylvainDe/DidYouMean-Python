# -*- coding: utf-8
"""Unit tests for didyoumean APIs."""
from didyoumean_api import didyoumean_decorator, didyoumean_contextmanager,\
    didyoumean_postmortem
from didyoumean_common_tests import TestWithStringFunction,\
    get_exception, no_exception, NoFileIoError
import unittest2
import sys
import os


class ApiTest(TestWithStringFunction):
    """ Tests about the didyoumean APIs. """

    def run_with_api(self, code):
        """ Abstract method to run code with tested API."""
        raise NotImplementedError()

    def get_exc_with_api(self, code):
        """ Get exception raised with running code with tested API."""
        try:
            self.run_with_api(code)
        except:
            return sys.exc_info()
        assert False, "No exception thrown"

    def get_exc_as_str(self, code, type_arg):
        """ Retrieve string representations of exceptions raised by code
        without and with the API. """
        type1, value1, _ = get_exception(code)
        self.assertTrue(isinstance(value1, type1))
        self.assertEqual(type_arg, type1)
        str1, repr1 = str(value1), repr(value1)
        type2, value2, _ = self.get_exc_with_api(code)
        self.assertTrue(isinstance(value2, type2))
        self.assertEqual(type_arg, type2)
        str2, repr2 = str(value2), repr(value2)
        return (str1, repr1, str2, repr2)

    def test_api_no_exception(self):
        """Check the case with no exception."""
        code = 'babar = 0\nbabar'
        no_exception(code)
        self.run_with_api(code)

    def test_api_suggestion(self):
        """Check the case with a suggestion."""
        type_ = NameError
        sugg = ". Did you mean 'babar' (local)?"
        code = 'babar = 0\nbaba'
        str1, repr1, str2, repr2 = self.get_exc_as_str(
            code, type_)
        self.assertStringAdded(sugg, str1, str2)
        self.assertStringAdded(sugg, repr1, repr2)

    def test_api_no_suggestion(self):
        """Check the case with no suggestion."""
        type_ = NameError
        sugg = ""
        code = 'babar = 0\nfdjhflsdsqfjlkqs'
        str1, repr1, str2, repr2 = self.get_exc_as_str(
            code, type_)
        self.assertStringAdded(sugg, str1, str2)
        self.assertStringAdded(sugg, repr1, repr2)

    def test_api_syntax(self):
        """Check the case with syntax error suggestion."""
        type_ = SyntaxError
        sugg = ". Did you mean to indent it, 'sys.exit([arg])'?"
        code = 'return'
        str1, repr1, str2, repr2 = self.get_exc_as_str(
            code, type_)
        self.assertStringAdded(sugg, str1, str2)
        # normalise quotes as they get changed at some point on PyPy
        self.assertStringAdded(
            sugg.replace("'", '"'),
            repr1.replace("'", '"'),
            repr2.replace("'", '"'))

    def test_api_ioerror(self):
        """Check the case with IO error suggestion."""
        type_ = NoFileIoError
        home = os.path.expanduser("~")
        sugg = ". Did you mean '" + home + "' (calling os.path.expanduser)?"
        code = 'with open("~") as f:\n\tpass'
        str1, repr1, str2, repr2 = self.get_exc_as_str(
            code, type_)
        self.assertStringAdded(sugg, str1, str2)
        self.assertStringAdded(
            sugg.replace("'", '"'),
            repr1.replace("'", '"'),
            repr2.replace("'", '"'))


class DecoratorTest(unittest2.TestCase, ApiTest):
    """ Tests about the didyoumean decorator. """

    def run_with_api(self, code):
        """ Run code with didyoumean decorator."""
        @didyoumean_decorator
        def my_func():
            exec(code) in globals(), locals()
        my_func()


class ContextManagerTest(unittest2.TestCase, ApiTest):
    """ Tests about the didyoumean context manager. """

    def run_with_api(self, code):
        """ Run code with didyoumean context manager."""
        with didyoumean_contextmanager():
            exec(code)


class PostMortemTest(unittest2.TestCase, ApiTest):
    """Tests about the didyoumean post mortem . """

    def run_with_api(self, code):
        """ Run code with didyoumean post mortem."""
        # A bit of an ugly way to proceed, in real life scenario
        # the sys.last_<something> members are set automatically.
        for a in ('last_type', 'last_value', 'last_traceback'):
            if hasattr(sys, a):
                delattr(sys, a)
        try:
            exec(code)
        except:
            sys.last_type, sys.last_value, sys.last_traceback = sys.exc_info()
        ret = didyoumean_postmortem()
        if ret is not None:
            raise ret


class HookTest(unittest2.TestCase):
    """ Tests about the didyoumean hook. """
    pass  # Can't write tests as the hook seems to be ignored.


if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
