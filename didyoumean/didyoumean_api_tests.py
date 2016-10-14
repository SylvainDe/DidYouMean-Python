# -*- coding: utf-8
"""Unit tests for didyoumean APIs."""
from didyoumean_api import didyoumean_decorator, didyoumean_contextmanager,\
    didyoumean_postmortem, didyoumean_enablehook, didyoumean_disablehook
from didyoumean_common_tests import TestWithStringFunction,\
    get_exception, no_exception, NoFileIoError
import unittest2
import sys
import os


class ApiTest(TestWithStringFunction):
    """Tests about the didyoumean APIs."""

    def run_with_api(self, code):
        """Abstract method to run code with tested API."""
        raise NotImplementedError("'run_with_api' needs to be implemented")

    def get_exc_with_api(self, code):
        """Get exception raised with running code with tested API."""
        try:
            self.run_with_api(code)
        except:
            return sys.exc_info()
        assert False, "No exception thrown"

    def get_exc_as_str(self, code, type_arg):
        """Retrieve string representations of exceptions raised by code.

        String representations are provided for the same code run
        with and without the API.
        """
        type1, value1, _ = get_exception(code)
        details1 = "%s %s" % (str(type1), str(value1))
        self.assertTrue(isinstance(value1, type1), details1)
        self.assertEqual(type_arg, type1, details1)
        str1, repr1 = str(value1), repr(value1)
        type2, value2, _ = self.get_exc_with_api(code)
        details2 = "%s %s" % (str(type2), str(value2))
        self.assertTrue(isinstance(value2, type2), details2)
        self.assertEqual(type_arg, type2, details2)
        str2, repr2 = str(value2), repr(value2)
        return (str1, repr1, str2, repr2)

    def check_sugg_added(self, code, type_, sugg, normalise_quotes=False):
        """Check that the suggestion gets added to the exception.

        Get the string representations for the exception before and after
        and check that the suggestion `sugg` is added to `before` to get
        `after`. `normalise_quotes` can be provided to replace all quotes
        by double quotes before checking the `repr()` representations as
        they may get changed sometimes.
        """
        str1, repr1, str2, repr2 = self.get_exc_as_str(
            code, type_)
        self.assertStringAdded(sugg, str1, str2, True)
        if normalise_quotes:
            sugg = sugg.replace("'", '"')
            repr1 = repr1.replace("'", '"')
            repr2 = repr2.replace("'", '"')
        self.assertStringAdded(sugg, repr1, repr2, True)

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
        self.check_sugg_added(code, type_, sugg)

    def test_api_no_suggestion(self):
        """Check the case with no suggestion."""
        type_ = NameError
        sugg = ""
        code = 'babar = 0\nfdjhflsdsqfjlkqs'
        self.check_sugg_added(code, type_, sugg)

    def test_api_syntax(self):
        """Check the case with syntax error suggestion."""
        type_ = SyntaxError
        sugg = ". Did you mean to indent it, 'sys.exit([arg])'?"
        code = 'return'
        self.check_sugg_added(code, type_, sugg, True)

    def test_api_ioerror(self):
        """Check the case with IO error suggestion."""
        type_ = NoFileIoError
        home = os.path.expanduser("~")
        sugg = ". Did you mean '" + home + "' (calling os.path.expanduser)?"
        code = 'with open("~") as f:\n\tpass'
        self.check_sugg_added(code, type_, sugg, True)


class DecoratorTest(unittest2.TestCase, ApiTest):
    """Tests about the didyoumean decorator."""

    def run_with_api(self, code):
        """Run code with didyoumean decorator."""
        @didyoumean_decorator
        def my_func():
            no_exception(code)
        my_func()


class ContextManagerTest(unittest2.TestCase, ApiTest):
    """Tests about the didyoumean context manager."""

    def run_with_api(self, code):
        """Run code with didyoumean context manager."""
        with didyoumean_contextmanager():
            no_exception(code)


class PostMortemTest(unittest2.TestCase, ApiTest):
    """Tests about the didyoumean post mortem."""

    def run_with_api(self, code):
        """Run code with didyoumean post mortem."""
        # A bit of an ugly way to proceed, in real life scenario
        # the sys.last_<something> members are set automatically.
        for a in ('last_type', 'last_value', 'last_traceback'):
            if hasattr(sys, a):
                delattr(sys, a)
        try:
            no_exception(code)
        except:
            sys.last_type, sys.last_value, sys.last_traceback = sys.exc_info()
        ret = didyoumean_postmortem()
        if ret is not None:
            raise ret


class HookTest(ApiTest):
    """Tests about the didyoumean hooks.

    These tests are somewhat artificial as one needs to explicitely catch
    the exception, simulate a call to the function that would have been
    called for an uncatched exception and reraise it (so that then it gets
    caught by yet another try-except).
    Realistically it might not catch any real-life problems (because these
    would happen when the shell does not behave as expected) but it might be
    useful to prevent regressions.
    """

    pass  # Can't write tests as the hook seems to be ignored.


class NotATest(object):
    """Dummy subclass to inherit from instead of unittest2.TestCase.

    The tests from ExceptHookTest are not very relevant most of the
    time and they flood the output because of the dodgy things we do
    with sys.excepthook. Most of the time, it is better not to run them
    but I still want to keep them for the time being. The solution is
    to be able to make this easily configurable by having the dependency
    over unittest2.TestCase optional with a simple test:
        class MyTest(unittest2.TestCase if <cond> else NotRunTest, ...)
    """

    pass


class ExceptHookTest(unittest2.TestCase if True else NotATest, HookTest):
    """Tests about the didyoumean excepthook."""

    def run_with_api(self, code):
        """Run code with didyoumean after enabling didyoumean hook."""
        prev_hook = sys.excepthook
        self.assertEqual(prev_hook, sys.excepthook)
        didyoumean_enablehook()
        self.assertNotEqual(prev_hook, sys.excepthook)
        try:
            no_exception(code)
        except:
            last_type, last_value, last_traceback = sys.exc_info()
            sys.excepthook(last_type, last_value, last_traceback)
            raise
        finally:
            self.assertNotEqual(prev_hook, sys.excepthook)
            didyoumean_disablehook()
            self.assertEqual(prev_hook, sys.excepthook)


class DummyShell:
    """Dummy class to emulate the iPython interactive shell.

    https://ipython.org/ipython-doc/dev/api/generated/IPython.core.interactiveshell.html
    """

    def __init__(self):
        """Init."""
        self.handler = None
        self.exc_tuple = None

    def set_custom_exc(self, exc_tuple, handler):
        """Emulate the interactiveshell.set_custom_exc method."""
        self.handler = handler
        self.exc_tuple = exc_tuple

    def showtraceback(self, exc_tuple=None,
                      filename=None, tb_offset=None, exception_only=False):
        """Emulate the interactiveshell.showtraceback method.

        Calls the custom exception handler if is it set.
        """
        if self.handler is not None and self.exc_tuple is not None:
            etype, evalue, tb = exc_tuple
            func, self.handler = self.handler, None  # prevent recursive calls
            func(self, etype, evalue, tb, tb_offset)
            self.handler = func

    def set(self, module):
        """Make shell accessible in module via 'get_ipython'."""
        assert 'get_ipython' not in dir(module)
        module.get_ipython = lambda: self

    def remove(self, module):
        """Make shell un-accessible in module via 'get_ipython'."""
        del module.get_ipython


class IPythonHookTest(unittest2.TestCase, HookTest):
    """Tests about the didyoumean custom exception handler for iPython.

    These tests need a dummy shell to be create to be able to use/define
    its functions related to the custom exception handlers.
    """

    def run_with_api(self, code):
        """Run code with didyoumean after enabling didyoumean hook."""
        prev_handler = None
        shell = DummyShell()
        module = sys.modules['didyoumean_api']
        shell.set(module)
        self.assertEqual(shell.handler, prev_handler)
        didyoumean_enablehook()
        self.assertNotEqual(shell.handler, prev_handler)
        try:
            no_exception(code)
        except:
            shell.showtraceback(sys.exc_info())
            raise
        finally:
            self.assertNotEqual(shell.handler, prev_handler)
            didyoumean_disablehook()
            self.assertEqual(shell.handler, prev_handler)
            shell.remove(module)
            shell = None


if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
