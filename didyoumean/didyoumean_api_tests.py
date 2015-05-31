# -*- coding: utf-8
"""Unit tests for didyoumean APIs."""
from didyoumean_decorator import didyoumean
from didyoumean_contextmanager import didyoumean_contextmanager
from didyoumean_common_tests import TestWithStringFunction,\
    get_exception, no_exception
import unittest2
import sys


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
        self.assertStringAdded(sugg, repr1, repr2, False)

    def test_api_no_suggestion(self):
        """Check the case with no suggestion."""
        type_ = NameError
        code = 'babar = 0\nfdjhflsdsqfjlkqs'
        str1, repr1, str2, repr2 = self.get_exc_as_str(
            code, type_)
        self.assertStringAdded("", str1, str2)
        self.assertStringAdded("", repr1, repr2)

    def test_api_syntax(self):
        """Check the case with syntax error suggestion."""
        type_ = SyntaxError
        sugg = ". Did you mean to indent it, 'sys.exit([arg])'?"
        code = 'return'
        str1, repr1, str2, repr2 = self.get_exc_as_str(
            code, type_)
        self.assertStringAdded(sugg, str1, str2, False)
        self.assertStringAdded(sugg, repr1, repr2, False)


class DecoratorTest(unittest2.TestCase, ApiTest):
    """ Tests about the didyoumean decorator. """

    def run_with_api(self, code):
        """ Run code with didyoumean decorator."""
        @didyoumean
        def my_func():
            exec(code) in globals(), locals()
        my_func()


class ContextManagerTest(unittest2.TestCase, ApiTest):
    """ Tests about the didyoumean context manager. """

    def run_with_api(self, code):
        """ Run code with didyoumean context manager."""
        with didyoumean_contextmanager():
            exec(code)

# def didyoumean_hook(type_, value, traceback, prev_hook=sys.excepthook):
#     """Hook to be substituted to sys.excepthook to enhance exceptions."""
#     add_suggestions_to_exception(type_, value, traceback)
#     return prev_hook(type_, value, traceback)
#
# class HookTest(unittest2.TestCase, ApiTest):
#     """ Tests about the didyoumean hook. """
#
#     def run_with_api(self, code):
#         """ Run code with didyoumean context manager."""
#         print(sys.__excepthook__ == sys.excepthook)
#         sys.excepthook = didyoumean_hook
#         print(sys.__excepthook__ == sys.excepthook)
#         exec(code)
#         print(sys.__excepthook__ == sys.excepthook)
#         sys.excepthook = sys.__excepthook__
#         print(sys.__excepthook__ == sys.excepthook)
#
if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
