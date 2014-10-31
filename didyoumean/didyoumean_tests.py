# -*- coding: utf-8
"""Unit tests for code in didyoumean.py."""
from didyoumean_decorator import didyoumean
import unittest
import math
import sys

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


def attributeerror_from_module():
    """Should be math.pi but I don't know how to manage this."""
    return math.pie


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


def attributeerror_from_class():
    """Should be 'this_is_cls_mthd'."""
    return FoobarClass().this_is_cls_mth


def typeerror_not_sub():
    """Should be 'inner_func(2)'."""
    def inner_func(foo):
        pass
    return inner_func[2]


def importerror_no_module():
    """Should be 'math'."""
    import maths


def importerror_no_module2():
    """Should be 'math'."""
    from maths import pi


def importerror_wrong_import():
    """Should be 'math'."""
    from itertools import pi


def importerror_typo_in_method():
    """Should be 'pi'."""
    from math import pie


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
    if name == 'attributeerror_from_module':
        return attributeerror_from_module()
    if name == 'attributeerror_from_class':
        return attributeerror_from_class()
    if name == 'typeerror_not_sub':
        return typeerror_not_sub()
    if name == 'importerror_no_module':
        return importerror_no_module()
    if name == 'importerror_no_module2':
        return importerror_no_module2()
    if name == 'importerror_wrong_import':
        return importerror_wrong_import()
    if name == 'importerror_typo_in_method':
        return importerror_typo_in_method()
    assert False


@didyoumean
def function_caller_deco(name):
    """Wrapper around function_caller with a didyoumean decorator."""
    return function_caller(name)


class AbstractTests(unittest.TestCase):
    """Generic class for unit tests."""

    def run_input(self, name, sugg):
        """Helper function to run tests."""
        name = self.error_prefix + '_' + name
        self.my_assert_raises_rexp(
            self.error_type,
            self.error_msg + "$",
            function_caller,
            name)
        self.my_assert_raises_rexp(
            self.error_type,
            self.error_msg + sugg + "$",
            function_caller_deco,
            name)

    def my_assert_raises_rexp(self, type_arg, message_re, callable_, *args, **kwds):
        """Substitute for TestCase.assertRaisesRegex as it is sometimes missing."""
        try:
            callable_(*args, **kwds)
        except:
            type_caught, value, traceback = sys.exc_info()
            if not issubclass(type_arg, type_caught):
                print(type_arg, type_caught)
            self.assertTrue(issubclass(type_arg, type_caught))
            self.assertRegexpMatches(''.join(value.args), message_re)
            return
        self.assertTrue(False)


class NameErrorTests(AbstractTests):
    """Class for tests related to NameError."""
    error_type = NameError
    error_msg = "^(global )?name '\w+' is not defined"
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
        self.run_input(
            'self2',
            ". Did you mean [^ ]*.this_is_cls_mthd, [^ ]*.this_is_cls_mthd")

    def test_cls(self):
        self.run_input(
            'cls',
            ". Did you mean [^ ]*.this_is_cls_mthd, [^ ]*.this_is_cls_mthd")


class AttributeErrorTest(AbstractTests):
    """Class for tests related to AttributeError."""
    error_type = AttributeError
    error_msg = "^'?\w+'? (object|instance) has no attribute '\w+'"
    error_prefix = 'attributeerror'

    def test_method(self):
        self.run_input('method', ". Did you mean append")

    def test_builtin(self):
        self.run_input('builtin', ". Did you mean max\\(list\\)")

    def test_no_sugg(self):
        self.run_input('no_sugg', "")

    def test_from_module(self):
        self.run_input('from_module', "")

    def test_from_class(self):
        self.run_input('from_class', ". Did you mean this_is_cls_mthd")


class TypeErrorTests(AbstractTests):
    """Class for tests related to TypeError."""
    error_type = TypeError
    error_prefix = 'typeerror'


class TypeErrorTestsNotSub(TypeErrorTests):
    """Class for tests related to substriptable."""
    error_msg = "^'\w+' object (is not subscriptable|has no attribute '__getitem__')"

    def test_not_sub(self):
        self.run_input('not_sub', ". Did you mean function\\(value\\)")


class ImportErrorTests(AbstractTests):
    """Class for tests related to ImportError."""
    error_type = ImportError
    error_prefix = 'importerror'


class ImportErrorTestsNoModule(ImportErrorTests):
    """Class for tests related to no module."""
    error_msg = "^No module named '?\w+'?"

    def test_no_module(self):
        self.run_input('no_module', ". Did you mean math")

    def test_no_module2(self):
        self.run_input('no_module2', ". Did you mean math")


class ImportErrorTestsCannotImport(ImportErrorTests):
    """Class for tests related to cannot import."""
    error_msg = "^cannot import name '?\w+'?"

    def test_wrong_import(self):
        self.run_input('wrong_import', "")

    def test_typo_in_method(self):
        self.run_input('typo_in_method', "")
