# -*- coding: utf-8
"""Unit tests for code in didyoumean.py."""
from didyoumean_decorator import didyoumean
import unittest

# Following code is bad on purpose - please do not fix ;-)

this_is_a_global_list = [1, 2]


def nameerror_1_arg(foo):
    """Should be 'return foo'."""
    return foob


def nameerror_n_args(fool, foot, bar):
    """Should be 'fool' or 'foot'."""
    return foob


def nameerror_builtin():
    """Should be 'max'."""
    return maxi


def nameerror_global():
    """Should be this_is_a_global_list."""
    return this_is_a_global_lis


def nameerror_no_sugg():
    """No suggestion."""
    return ldkjhfnvdlkjhvgfdhgf


def nameerror_import_sugg():
    """Should import functools first."""
    return functools.wraps


def attributeerror_method():
    """Should be 'append'."""
    lst = [1, 2, 3]
    lst.appendh(4)


def attributeerror_builtin():
    """Should be 'max(lst)'."""
    lst = [1, 2, 3]
    lst.max()


def attributeerror_no_sugg():
    """No suggestion."""
    lst = [1, 2, 3]
    lst.ldkjhfnvdlkjhvgfdhgf


class FoobarClass():
    """Dummy class for testing purposes."""

    def __init__(self):
        """Constructor."""
        self.foo = 4
        self.bar = 2

    @classmethod
    def this_is_cls_mthd(cls):
        """Just a class method."""
        return 5

    def nameerror_self(self):
        """Should be self.foo."""
        return foo

    def nameerror_self2(self):
        """Should be self.this_is_cls_mthd (or FoobarClass)."""
        return this_is_cls_mthd

    @classmethod
    def nameerror_cls(cls):
        """Should be cls.this_is_cls_mthd (or FoobarClass)."""
        return this_is_cls_mthd


def function_caller(name):
    """Dirty function to call test function without bothering about arguments
    or instances."""
    if name == 'nameerror_1_arg':
        return nameerror_1_arg(1)
    if name == 'nameerror_n_args':
        return nameerror_n_args(1, 2, 3)
    if name == 'nameerror_builtin':
        return nameerror_builtin()
    if name == 'nameerror_global':
        return nameerror_global()
    if name == 'nameerror_no_sugg':
        return nameerror_no_sugg()
    if name == 'nameerror_import_sugg':
        return nameerror_import_sugg()
    if name == 'nameerror_self':
        return FoobarClass().nameerror_self()
    if name == 'nameerror_self2':
        return FoobarClass().nameerror_self2()
    if name == 'nameerror_cls':
        return FoobarClass().nameerror_cls()
    if name == 'attributeerror_builtin':
        return attributeerror_builtin()
    if name == 'attributeerror_method':
        return attributeerror_method()
    if name == 'attributeerror_no_sugg':
        return attributeerror_no_sugg()


@didyoumean
def function_caller_deco(name):
    """Wrapper around function_caller with a didyoumean decorator."""
    return function_caller(name)


class AbstractTests(unittest.TestCase):
    """Generic class for unit tests."""

    def run_input(self, name, sugg):
        """Helper function to run tests."""
        name = self.error_prefix + '_' + name
        self.assertRaisesRegex(
            self.error_type,
            self.error_msg + "$",
            lambda: function_caller(name))
        self.assertRaisesRegex(
            self.error_type,
            self.error_msg + sugg + "$",
            lambda: function_caller_deco(name))


class NameErrorTests(AbstractTests):
    """Class for tests related to NameError."""
    error_type = NameError
    error_msg = "^(global )?name '[^']*' is not defined"
    error_prefix = 'nameerror'

    def test_1_arg(self):
        self.run_input('1_arg', ". Did you mean foo")

    def test_n_args(self):
        self.run_input('n_args', ". Did you mean foot, fool")

    def test_builtin(self):
        self.run_input('builtin', ". Did you mean max")

    def test_global(self):
        self.run_input('global', ". Did you mean this_is_a_global_list")

    def test_no_sugg(self):
        self.run_input('no_sugg', "")

    def test_import_sugg(self):
        self.run_input('import_sugg', ". Did you mean import functools")

    def test_self(self):
        self.run_input('self', ". Did you mean self.foo")

    def test_self2(self):
        self.run_input('self2', ". Did you mean [^ ]*.this_is_cls_mthd, [^ ]*.this_is_cls_mthd")

    def test_cls(self):
        self.run_input('cls', ". Did you mean [^ ]*.this_is_cls_mthd, [^ ]*.this_is_cls_mthd")


class AttributeErrorTest(AbstractTests):
    """Class for tests related to AttributeError."""
    error_type = AttributeError
    error_msg = "^'[^']*' object has no attribute '[^']*'"
    error_prefix = 'attributeerror'

    def test_method(self):
        self.run_input('method', ". Did you mean append")

    def test_builtin(self):
        self.run_input('builtin', ". Did you mean max\\(list\\)")

    def test_no_sugg(self):
        self.run_input('no_sugg', "")
