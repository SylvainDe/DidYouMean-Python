# -*- coding: utf-8
"""Unit tests for code in didyoumean.py."""
from didyoumean_decorator import didyoumean
import unittest2
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


def nameerror_keyword():
    """Should be 'yield'."""
    yieldd


def nameerror_global():
    """Should be this_is_a_global_list."""
    return this_is_a_global_lis


def nameerror_import():
    """Should be math.pi."""
    return maths.pi


def nameerror_import2():
    """Should be my_imported_math.pi."""
    import math as my_imported_math
    return my_imported_maths.pi


def nameerror_imported():
    """Should be math.pi."""
    return pi


def nameerror_no_sugg():
    """No suggestion."""
    return ldkjhfnvdlkjhvgfdhgf


def nameerror_import_sugg():
    """Should import functools first."""
    return functools.wraps


def nameerror_removed_1():
    """Builtin cmp is removed."""
    return cmp(1, 2)


def unboundlocalerror_1():
    """Should be foo."""
    foo = 1
    foob += 1
    return foo


def attributeerror_method():
    """Should be 'append'."""
    [1, 2, 3].appendh(4)


def attributeerror_builtin():
    """Should be 'max(lst)'."""
    [1, 2, 3].max()


def my_generator():
    """This is my generator.
    This is my generator, baby."""
    while True:
        yield 1


def attributeerror_builtin2():
    """Should be 'next(gen)'."""
    return my_generator().next()


def attributeerror_wrongmethod():
    """Should be 'lst.append(4)'."""
    [1, 2, 3].add(4)


def attributeerror_wrongmethod2():
    """Should be 'lst.extend([4, 5, 6])'."""
    [1, 2, 3].update([4, 5, 6])

def attributeerror_hidden():
    """Accessing wrong string object."""
    import string
    string = 'a'
    return string.ascii_letters

def attributeerror_no_sugg():
    """No suggestion."""
    [1, 2, 3].ldkjhfnvdlkjhvgfdhgf


def attributeerror_from_module(radius=1):
    """Should be math.pi."""
    return 2 * math.pie * radius


class FoobarClass():
    """Dummy class for testing purposes."""

    def __init__(self):
        """Constructor."""
        self.bar = 2

    @classmethod
    def this_is_cls_mthd(cls):
        """Just a class method."""
        return 5

    def nameerror_self(self):
        """Should be self.bar."""
        return bar

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


def attributeerror_removed_1():
    """Method has_key is removed from dict."""
    return dict().has_key(1)


def typeerror_not_sub():
    """Should be 'inner_func(2)'."""
    def inner_func(foo):
        pass
    return inner_func[2]


def importerror_no_module_no_sugg():
    """No suggestion."""
    import fqslkdfjslkqdjfqsd


def importerror_no_module():
    """Should be 'math'."""
    import maths


def importerror_no_module2():
    """Should be 'math'."""
    from maths import pi


def importerror_no_module3():
    """Should be 'math'."""
    import maths as my_imported_math


def importerror_no_module4():
    """Should be 'math'."""
    from maths import pi as three_something


def importerror_no_name_suggested():
    """No suggestion."""
    from math import fsfsdfdjlkf


def importerror_wrong_import():
    """Should be 'math'."""
    from itertools import pi


def importerror_typo_in_method():
    """Should be 'pi'."""
    from math import pie


def importerror_typo_in_method2():
    """Should be 'pi'."""
    from math import e, pie, log


def importerror_typo_in_method3():
    """Should be 'pi'."""
    from math import pie as three_something


def keyerror_no_sugg():
    """No suggestion."""
    dct = dict()
    return dct['ffdsqmjklfqsd']


def indexerror_no_sugg():
    """No suggestion."""
    lst = [1]
    return lst[2]


# Logic to be able to have different tests on various version of Python
FIRST_VERSION = (0, 0)
LAST_VERSION = (10, 0)
ALL_VERSIONS = (FIRST_VERSION, LAST_VERSION)


def from_version(version):
    return (version, LAST_VERSION)


def up_to_version(version):
    return (FIRST_VERSION, version)


# Wrappers to eval some code with or without a decorator."""
def eval_wrapper(code):
    """Dirty function to eval some code."""
    eval(code)


@didyoumean
def eval_wrapper_deco(code):
    """Wrapper around eval_wrapper with a didyoumean decorator."""
    return eval_wrapper(code)


# Tests
class AbstractTests(unittest2.TestCase):
    """Generic class for unit tests."""

    def code_runs(self, code, version_range=ALL_VERSIONS):
        """Helper function to run code and check it works."""
        beg, end = version_range
        if beg <= sys.version_info < end:
            eval_wrapper(code)
            eval_wrapper_deco(code)

    def code_throws(self, code, sugg, version_range=ALL_VERSIONS):
        """Helper function to run code and check is throws."""
        beg, end = version_range
        if beg <= sys.version_info < end:
            self.my_assert_raises_rexp(
                self.error_type,
                self.error_msg + "$",
                eval_wrapper,
                code)
            self.my_assert_raises_rexp(
                self.error_type,
                self.error_msg + sugg + "$",
                eval_wrapper_deco,
                code)

    def my_assert_raises_rexp(self, type_arg, message_re, callable_, *args, **kwds):
        """Substitute for TestCase.assertRaisesRegex as it is sometimes missing."""
        try:
            callable_(*args, **kwds)
        except:
            type_caught, value, traceback = sys.exc_info()
            self.assertTrue(issubclass(type_arg, type_caught))
            self.assertRegexpMatches(''.join(value.args[0]), message_re)
            return
        self.assertTrue(False)


class NameErrorTests(AbstractTests):
    """Class for tests related to NameError."""
    error_type = NameError
    error_msg = "^(global )?name '\w+' is not defined"

    def test_1_arg(self):
        self.code_throws('nameerror_1_arg(1)', ". Did you mean 'foo'\?")

    def test_n_args(self):
        self.code_throws('nameerror_n_args(1, 2, 3)', ". Did you mean 'foot', 'fool'\?")

    def test_builtin(self):
        self.code_throws('nameerror_builtin()', ". Did you mean 'max'\?")

    def test_keyword(self):
        self.code_throws('nameerror_keyword()', ". Did you mean 'yield'\?")

    def test_global(self):
        self.code_throws('nameerror_global()', ". Did you mean 'this_is_a_global_list'\?")

    def test_import(self):
        self.code_throws('nameerror_import()', ". Did you mean 'math'\?")

    def test_import2(self):
        self.code_throws('nameerror_import2()', ". Did you mean 'my_imported_math'\?")

    def test_imported(self):
        self.code_throws('nameerror_imported()', ". Did you mean 'math.pi'\?")

    def test_no_sugg(self):
        self.code_throws('nameerror_no_sugg()', "")

    def test_removed_1(self):
        code = 'nameerror_removed_1()'
        version = (3, 0, 1)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))

    def test_import_sugg(self):
        self.code_throws('nameerror_import_sugg()', ". Did you mean to import functools first\?")

    def test_self(self):
        self.code_throws('FoobarClass().nameerror_self()', ". Did you mean 'self.bar'\?")

    def test_self2(self):
        self.code_throws(
            'FoobarClass().nameerror_self2()',
            ". Did you mean '[^ ]*.this_is_cls_mthd', '[^ ]*.this_is_cls_mthd'\?")

    def test_cls(self):
        self.code_throws(
            'FoobarClass().nameerror_cls()',
            ". Did you mean '[^ ]*.this_is_cls_mthd', '[^ ]*.this_is_cls_mthd'\?")


class UnboundLocalErrorTests(AbstractTests):
    """Class for tests related to UnboundLocalError."""
    error_type = UnboundLocalError
    error_msg = "^local variable '\w+' referenced before assignment"

    def test_1(self):
        self.code_throws('unboundlocalerror_1()', ". Did you mean 'foo'\?")


class AttributeErrorTest(AbstractTests):
    """Class for tests related to AttributeError."""
    error_type = AttributeError
    error_msg = "^'?\w+'? (object|instance) has no attribute '\w+'"

    def test_method(self):
        self.code_throws('attributeerror_method()', ". Did you mean 'append'\?")

    def test_builtin(self):
        self.code_throws('attributeerror_builtin()', ". Did you mean 'max\\(list\\)'\?")

    def test_builtin2(self):
        code = 'attributeerror_builtin2()'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, ". Did you mean 'next\\(generator\\)'\?", from_version(version))

    def test_wrongmethod(self):
        self.code_throws('attributeerror_wrongmethod()', ". Did you mean 'append'\?")

    def test_wrongmethod2(self):
        self.code_throws('attributeerror_wrongmethod2()', ". Did you mean 'extend'\?")

    def test_hidden(self):
        self.code_throws('attributeerror_hidden()', "")

    def test_no_sugg(self):
        self.code_throws('attributeerror_no_sugg()', "")

    def test_from_module(self):
        self.code_throws('attributeerror_from_module()', ". Did you mean 'pi'\?")

    def test_from_class(self):
        self.code_throws('attributeerror_from_class()', ". Did you mean 'this_is_cls_mthd'\?")

    def test_removed_1(self):
        code = 'attributeerror_removed_1()'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))


class TypeErrorTests(AbstractTests):
    """Class for tests related to TypeError."""
    error_type = TypeError


class TypeErrorTestsNotSub(TypeErrorTests):
    """Class for tests related to substriptable."""
    error_msg = "^'\w+' object (is (not |un)subscriptable|has no attribute '__getitem__')"

    def test_not_sub(self):
        self.code_throws('typeerror_not_sub()', ". Did you mean 'function\\(value\\)'\?")


class ImportErrorTests(AbstractTests):
    """Class for tests related to ImportError."""
    error_type = ImportError


class ImportErrorTestsNoModule(ImportErrorTests):
    """Class for tests related to no module."""
    error_msg = "^No module named '?\w+'?"

    def test_no_module_no_sugg(self):
        self.code_throws('importerror_no_module_no_sugg()', "")

    def test_no_module(self):
        self.code_throws('importerror_no_module()', ". Did you mean 'math'\?")

    def test_no_module2(self):
        self.code_throws('importerror_no_module2()', ". Did you mean 'math'\?")

    def test_no_module3(self):
        self.code_throws('importerror_no_module2()', ". Did you mean 'math'\?")

    def test_no_module4(self):
        self.code_throws('importerror_no_module2()', ". Did you mean 'math'\?")


class ImportErrorTestsCannotImport(ImportErrorTests):
    """Class for tests related to cannot import."""
    error_msg = "^cannot import name '?\w+'?"

    def test_no_name_no_sugg(self):
        self.code_throws('importerror_no_name_suggested()', "")

    def test_wrong_import(self):
        self.code_throws('importerror_wrong_import()', ". Did you mean 'from math import pi'\?")

    def test_typo_in_method(self):
        self.code_throws('importerror_typo_in_method()', ". Did you mean 'pi'\?")

    def test_typo_in_method2(self):
        self.code_throws('importerror_typo_in_method2()', ". Did you mean 'pi'\?")

    def test_typo_in_method3(self):
        self.code_throws('importerror_typo_in_method2()', ". Did you mean 'pi'\?")


class LookupErrorTests(AbstractTests):
    """Class for tests related to LookupError."""
    error_type = LookupError


class KeyErrorTests(LookupErrorTests):
    """Class for tests related to KeyError."""
    error_type = KeyError
    error_msg = ''

    def test_no_sugg(self):
        self.code_throws('keyerror_no_sugg()', "")


class IndexErrorTests(LookupErrorTests):
    """Class for tests related to IndexError."""
    error_type = IndexError
    error_msg = "^list index out of range"

    def test_no_sugg(self):
        self.code_throws('indexerror_no_sugg()', "")


class SyntaxErrorTests(AbstractTests):
    """Class for tests related to SyntaxError."""
    error_type = SyntaxError
    error_msg = 'invalid syntax'

    def test_print(self):
        code = 'print "a"'
        version = (3, 0)
        self.code_throws(code, "", up_to_version(version))  # WHY ?
        self.code_throws(code, "", from_version(version))

    def test_old_comparison(self):
        code = '1 <> 2'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))
