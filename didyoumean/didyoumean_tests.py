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


def nameerror_import2():
    """Should be my_imported_math.pi."""
    import math as my_imported_math
    return my_imported_maths.pi


def nameerror_attribute_hidden():
    """Should be math.pi but module math is hidden."""
    math = ''
    return pi


def unboundlocalerror_1():
    """Should be foo."""
    foo = 1
    foob += 1
    return foo


def my_generator():
    """This is my generator.
    This is my generator, baby."""
    while True:
        yield 1


def attributeerror_hidden():
    """Accessing wrong string object."""
    import string
    string = 'a'
    return string.ascii_letters


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

    def some_method(self):
        pass


def attributeerror_removed_xreadlines():
    """Method xreadlines from dict."""
    import os
    with open(os.path.realpath(__file__)) as f:
        for l in f.xreadlines():
            pass


def some_func(foo):
    """Dummy function for testing purposes."""
    pass


# Logic to be able to have different tests on various version of Python
FIRST_VERSION = (0, 0)
LAST_VERSION = (10, 0)
ALL_VERSIONS = (FIRST_VERSION, LAST_VERSION)


def from_version(version):
    return (version, LAST_VERSION)


def up_to_version(version):
    return (FIRST_VERSION, version)


# Wrappers to exec some code with or without a decorator."""
def exec_wrapper(code):
    """Dirty function to exec some code."""
    exec(code)


@didyoumean
def exec_wrapper_deco(code):
    """Dirty function to exec some code with a didyoumean decorator."""
    exec(code)


# Tests
class AbstractTests(unittest2.TestCase):
    """Generic class for unit tests."""
    error_msg = ''

    def code_runs(self, code, version_range=ALL_VERSIONS):
        """Helper function to run code and check it works."""
        beg, end = version_range
        if beg <= sys.version_info < end:
            exec_wrapper(code)
            exec_wrapper_deco(code)

    def code_throws(self, code, sugg, version_range=ALL_VERSIONS):
        """Helper function to run code and check is throws."""
        beg, end = version_range
        if beg <= sys.version_info < end:
            self.my_assert_raises_rexp(
                self.error_type,
                self.error_msg + "$",
                exec_wrapper,
                code)
            self.my_assert_raises_rexp(
                self.error_type,
                self.error_msg + sugg + "$",
                exec_wrapper_deco,
                code)

    def my_assert_raises_rexp(self, type_arg, message_re, func, *args, **kwds):
        """Substitute for TestCase.assertRaisesRegex
        because it is sometimes missing."""
        try:
            func(*args, **kwds)
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
        self.code_throws(
            'nameerror_n_args(1, 2, 3)', ". Did you mean 'foot', 'fool'\?")

    def test_builtin(self):
        """Should be 'max'."""
        self.code_throws('m = maxi', ". Did you mean 'max'\?")
        self.code_runs('m = max')

    def test_keyword(self):
        """Should be 'yield'."""
        self.code_throws('yieldd', ". Did you mean 'yield'\?")

    def test_global(self):
        """Should be this_is_a_global_list."""
        self.code_throws(
            'a = this_is_a_global_lis',
            ". Did you mean 'this_is_a_global_list'\?")
        self.code_runs('a = this_is_a_global_list')

    def test_import(self):
        """Should be math.pi."""
        self.code_throws('p = maths.pi', ". Did you mean 'math'\?")
        self.code_runs('p = math.pi')

    def test_import2(self):
        self.code_throws(
            'nameerror_import2()', ". Did you mean 'my_imported_math'\?")

    def test_imported(self):
        """Should be math.pi."""
        self.code_throws('p = pi', ". Did you mean 'math.pi'\?")
        self.code_runs('p = math.pi')

    def test_no_sugg(self):
        """No suggestion."""
        self.code_throws('a = ldkjhfnvdlkjhvgfdhgf', "")

    def test_removed_cmp(self):
        """Builtin cmp is removed."""
        code = 'cmp(1, 2)'
        version = (3, 0, 1)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))

    def test_removed_reduce(self):
        """Builtin reduce is removed - moved to functools."""
        code = 'reduce(lambda x, y: x + y, [1, 2, 3, 4, 5])'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))

    def test_removed_apply(self):
        """Builtin apply is removed."""
        code = 'apply(sum, [[1, 2, 3]])'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))

    def test_removed_intern(self):
        """Builtin intern is removed - moved to sys."""
        code = 'intern("toto")'
        new_code = 'sys.intern("toto")'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(
            code,
            ". Did you mean 'sys.intern', 'iter'\?",
            from_version(version))
        self.code_runs(new_code, from_version(version))

    def test_removed_execfile(self):
        """Builtin execfile is removed - use exec() and compile()."""
        code = 'execfile("some_filename")'
        version = (3, 0)
        # self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))

    def test_removed_raw_input(self):
        """Builtin raw_input is removed - use input() instead."""
        code = 'i = raw_input("Prompt:")'
        version = (3, 0)
        # self.code_runs(code, up_to_version(version))
        self.code_throws(
            code,
            ". Did you mean 'input'\?",
            from_version(version))

    def test_removed_buffer(self):
        """Builtin buffer is removed - use memoryview instead."""
        code = 'buffer("abc")'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))

    def test_import_sugg(self):
        """Should import functools first."""
        self.code_throws(
            'w = functools.wraps',
            ". Did you mean to import functools first\?")

    def test_attribute_hidden(self):
        self.code_throws(
            'nameerror_attribute_hidden()',
            ". Did you mean 'math.pi' \(hidden\)\?")

    def test_self(self):
        self.code_throws(
            'FoobarClass().nameerror_self()', ". Did you mean 'self.bar'\?")

    def test_self2(self):
        self.code_throws(
            'FoobarClass().nameerror_self2()',
            (". Did you mean '[^ ]*.this_is_cls_mthd', "
             "'[^ ]*.this_is_cls_mthd'\?"))

    def test_cls(self):
        self.code_throws(
            'FoobarClass().nameerror_cls()',
            (". Did you mean '[^ ]*.this_is_cls_mthd', "
             "'[^ ]*.this_is_cls_mthd'\?"))


class UnboundLocalErrorTests(AbstractTests):
    """Class for tests related to UnboundLocalError."""
    error_type = UnboundLocalError
    error_msg = "^local variable '\w+' referenced before assignment"

    def test_1(self):
        self.code_throws('unboundlocalerror_1()', ". Did you mean 'foo'\?")


class AttributeErrorTest(AbstractTests):
    """Class for tests related to AttributeError."""
    error_type = AttributeError
    error_msg = "^'?[\w\.]+'? (object|instance) has no attribute '\w+'"

    def test_nonetype(self):
        """In-place methods like sort returns None.
        Might also happen if the functions misses a return."""
        self.code_throws(
            '[3, 2, 1].sort().append(4)', "")

    def test_method(self):
        """Should be 'append'."""
        self.code_throws(
            '[1, 2, 3].appendh(4)', ". Did you mean 'append'\?")
        self.code_runs('[1, 2, 3].append(4)')

    def test_builtin(self):
        """Should be 'max(lst)'."""
        self.code_throws(
            '[1, 2, 3].max()', ". Did you mean 'max\\(list\\)'\?")
        self.code_runs('max([1, 2, 3])')

    def test_builtin2(self):
        """Should be 'next(gen)'."""
        code = 'my_generator().next()'
        new_code = 'next(my_generator())'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(
            code,
            ". Did you mean 'next\\(generator\\)'\?",
            from_version(version))
        self.code_runs(new_code)

    def test_wrongmethod(self):
        """Should be 'lst.append(4)'."""
        self.code_throws(
            '[1, 2, 3].add(4)', ". Did you mean 'append'\?")
        self.code_runs('[1, 2, 3].append(4)')

    def test_wrongmethod2(self):
        """Should be 'lst.extend([4, 5, 6])'."""
        self.code_throws(
            '[1, 2, 3].update([4, 5, 6])', ". Did you mean 'extend'\?")
        self.code_runs('[1, 2, 3].extend([4, 5, 6])')

    def test_hidden(self):
        self.code_throws('attributeerror_hidden()', "")

    def test_no_sugg(self):
        """No suggestion."""
        self.code_throws('[1, 2, 3].ldkjhfnvdlkjhvgfdhgf', "")

    def test_from_module(self):
        self.code_throws(
            'attributeerror_from_module()', ". Did you mean 'pi'\?")

    def test_from_class(self):
        """Should be 'this_is_cls_mthd'."""
        self.code_throws(
            'FoobarClass().this_is_cls_mth()',
            ". Did you mean 'this_is_cls_mthd'\?")

    def test_removed_has_key(self):
        """Method has_key is removed from dict."""
        code = 'dict().has_key(1)'
        new_code = '1 in dict()'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(
            code, ". Did you mean 'key in dict'\?", from_version(version))
        self.code_runs(new_code)

    def test_removed_xreadlines(self):
        code = 'attributeerror_removed_xreadlines()'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))

    def test_removed_function_attributes(self):
        version = (3, 0)
        func_name = 'some_func'
        attributes = [('func_name', '__name__'),
                      ('func_doc', '__doc__'),
                      ('func_defaults', '__defaults__'),
                      ('func_dict', '__dict__'),
                      ('func_closure', '__closure__'),
                      ('func_globals', '__globals__'),
                      ('func_code', '__code__')]
        for (old_att, new_att) in attributes:
            old_code = func_name + '.' + old_att
            new_code = func_name + '.' + new_att
            self.code_runs(old_code, up_to_version(version))
            self.code_throws(old_code, "", from_version(version))
            self.code_runs(new_code)

    def test_removed_method_attributes(self):
        version = (3, 0)
        meth_name = 'FoobarClass().some_method'
        attributes = [('im_func', '__func__'),
                      ('im_self', '__self__'),
                      ('im_class', '__self__.__class__')]
        for (old_att, new_att) in attributes:
            old_code = meth_name + '.' + old_att
            new_code = meth_name + '.' + new_att
            self.code_runs(old_code, up_to_version(version))
            self.code_throws(old_code, "", from_version(version))
            self.code_runs(new_code)


class TypeErrorTests(AbstractTests):
    """Class for tests related to TypeError."""
    error_type = TypeError


class TypeErrorTestsNotSub(TypeErrorTests):
    """Class for tests related to substriptable."""
    error_msg = ("^'\w+' object (is (not |un)subscriptable"
                 "|has no attribute '__getitem__')")

    def test_not_sub(self):
        """Should be 'some_func(2)'."""
        self.code_throws(
            'some_func[2]', ". Did you mean 'function\\(value\\)'\?")


class TypeErrorTestsNumberArgs(TypeErrorTests):
    """Class for tests related to number of arguments."""

    def test_nb_args(self):
        """Should be 'some_func(1)'."""
        self.code_throws('some_func(1, 2)', "")


class ImportErrorTests(AbstractTests):
    """Class for tests related to ImportError."""
    error_type = ImportError


class ImportErrorTestsNoModule(ImportErrorTests):
    """Class for tests related to no module."""
    error_msg = "^No module named '?\w+'?"

    def test_no_module_no_sugg(self):
        """No suggestion."""
        self.code_throws('import fqslkdfjslkqdjfqsd', "")

    def test_no_module(self):
        """Should be 'math'."""
        self.code_throws('import maths', ". Did you mean 'math'\?")
        self.code_runs('import math')

    def test_no_module2(self):
        """Should be 'math'."""
        self.code_throws(
            'from maths import pi', ". Did you mean 'math'\?")
        self.code_runs('from math import pi')

    def test_no_module3(self):
        """Should be 'math'."""
        self.code_throws(
            'import maths as my_imported_math', ". Did you mean 'math'\?")
        self.code_runs('import math as my_imported_math')

    def test_no_module4(self):
        """Should be 'math'."""
        self.code_throws(
            'from maths import pi as three_something',
            ". Did you mean 'math'\?")
        self.code_runs('from math import pi as three_something')


class ImportErrorTestsCannotImport(ImportErrorTests):
    """Class for tests related to cannot import."""
    error_msg = "^cannot import name '?\w+'?"

    def test_no_name_no_sugg(self):
        """No suggestion."""
        self.code_throws('from math import fsfsdfdjlkf', "")

    def test_wrong_import(self):
        """Should be 'math'."""
        self.code_throws(
            'from itertools import pi',
            ". Did you mean 'from math import pi'\?")
        self.code_runs('from math import pi')

    def test_typo_in_method(self):
        """Should be 'pi'."""
        self.code_throws(
            'from math import pie', ". Did you mean 'pi'\?")
        self.code_runs('from math import pi')

    def test_typo_in_method2(self):
        """Should be 'pi'."""
        self.code_throws(
            'from math import e, pie, log', ". Did you mean 'pi'\?")
        self.code_runs('from math import e, pi, log')

    def test_typo_in_method3(self):
        """Should be 'pi'."""
        self.code_throws(
            'from math import pie as three_something', ". Did you mean 'pi'\?")
        self.code_runs('from math import pi as three_something')


class LookupErrorTests(AbstractTests):
    """Class for tests related to LookupError."""
    error_type = LookupError


class KeyErrorTests(LookupErrorTests):
    """Class for tests related to KeyError."""
    error_type = KeyError

    def test_no_sugg(self):
        """No suggestion."""
        self.code_throws('dict()["ffdsqmjklfqsd"]', "")


class IndexErrorTests(LookupErrorTests):
    """Class for tests related to IndexError."""
    error_type = IndexError
    error_msg = "^list index out of range"

    def test_no_sugg(self):
        """No suggestion."""
        self.code_throws('list()[2]', "")


class SyntaxErrorTests(AbstractTests):
    """Class for tests related to SyntaxError."""
    error_type = SyntaxError

    def test_no_error(self):
        self.code_runs("1 + 2 == 2")

    def test_yield_return_out_of_func(self):
        self.code_throws("yield 1", "")
        self.code_throws("return 1", "")

    def test_print(self):
        code = 'print "a"'
        new_code = 'print("a")'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))
        self.code_runs(new_code)

    def test_exec(self):
        code = 'exec "some_python_code = 1"'
        new_code = 'exec("some_python_code = 1")'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))
        self.code_runs(new_code)

    def test_old_comparison(self):
        code = '1 <> 2'
        new_code = '1 != 2'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, ". Did you mean '!='\?", from_version(version))
        self.code_runs(new_code)


class ValueErrorTests(AbstractTests):
    """Class for tests related to ValueError."""
    error_type = ValueError

    def test_too_many_values(self):
        self.code_throws('a, b, c = [1, 2, 3, 4]', "")

    def test_not_enough_values(self):
        self.code_throws('a, b, c = [1, 2]', "")

    def test_conversion_fails(self):
        self.code_throws('int("toto")', "")

    def test_math_domain(self):
        self.code_throws('lg = math.log(-1)', "")

if __name__ == '__main__':
    unittest2.main()
