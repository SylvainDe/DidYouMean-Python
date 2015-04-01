# -*- coding: utf-8
"""Unit tests for code in didyoumean.py."""
from didyoumean_decorator import didyoumean
from didyoumean_re import UNBOUNDERROR_RE, NAMENOTDEFINED_RE,\
    ATTRIBUTEERROR_RE, UNSUBSCRIBTABLE_RE, UNEXPECTED_KEYWORDARG_RE,\
    NOMODULE_RE, CANNOTIMPORT_RE, INDEXOUTOFRANGE_RE
import unittest2
import math
import sys

# Following code is bad on purpose - please do not fix ;-)

this_is_a_global_list = [1, 2]


def my_generator():
    """This is my generator.
    This is my generator, baby."""
    while True:
        yield 1


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


def some_func(foo):
    """Dummy function for testing purposes."""
    pass


def some_func2(abcdef=None):
    """Dummy function for testing purposes."""
    pass


# Logic to be able to have different tests on various version of Python
FIRST_VERSION = (0, 0)
LAST_VERSION = (10, 0)
ALL_VERSIONS = (FIRST_VERSION, LAST_VERSION)


def from_version(version):
    """Create tuple describing a range of versions from a given version."""
    return (version, LAST_VERSION)


def up_to_version(version):
    """Create tuple describing a range of versions up to a given version."""
    return (FIRST_VERSION, version)


def format_str(template, *args):
    """Format multiple string by using first arg as a template."""
    return [template.format(arg) for arg in args]


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
        """Helper function to run code and check it throws."""
        beg, end = version_range
        if beg <= sys.version_info < end:
            self.my_assert_raises_rexp(
                self.error_type,
                self.error_msg + "$",
                exec_wrapper,
                code)
            self.my_assert_raises_rexp(
                self.error_type,
                self.get_error_msg_to_be_expanded() + sugg + "$",
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

    def get_error_msg_to_be_expanded(self):
        """Remove final '$' from error message regexp to expand it."""
        msg = self.error_msg
        # I'd like to "assert msg.endswith('$')" at some point but not now...
        if msg.endswith('$'):
            return msg[:-1]
        return msg


class NameErrorTests(AbstractTests):
    """Class for tests related to NameError."""
    error_type = NameError
    error_msg = NAMENOTDEFINED_RE

    def test_local(self):
        """Should be 'foo'."""
        code = "foo = 0\n{0}"
        typo, sugg = "foob", "foo"
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_1_arg(self):
        """Should be 'foo'."""
        code = "def func(foo):\n\t{0}\nfunc(1)"
        typo, sugg = "foob", "foo"
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_n_args(self):
        """Should be 'fool' or 'foot'."""
        code = "def func(fool, foot, bar):\n\t{0}\nfunc(1, 2, 3)"
        typo, sugg1, sugg2 = "foob", "foot", "fool"
        bad, good1, good2 = format_str(code, typo, sugg1, sugg2)
        self.code_throws(bad, ". Did you mean 'foot', 'fool'\?")
        self.code_runs(good1)
        self.code_runs(good2)

    def test_builtin(self):
        """Should be 'max'."""
        typo, sugg = 'maxi', 'max'
        self.code_throws(typo, ". Did you mean '" + sugg + "'\?")
        self.code_runs(sugg)

    def test_keyword(self):
        """Should be 'pass'."""
        typo, sugg = 'passs', 'pass'
        self.code_throws(typo, ". Did you mean '" + sugg + "'\?")
        self.code_runs(sugg)

    def test_global(self):
        """Should be this_is_a_global_list."""
        typo, sugg = 'this_is_a_global_lis', 'this_is_a_global_list'
        self.code_throws(typo, ". Did you mean '" + sugg + "'\?")
        self.code_runs(sugg)

    def test_import(self):
        """Should be math.pi."""
        code = '{0}.pi'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_import2(self):
        """Should be my_imported_math.pi."""
        code = 'import math as my_imported_math\n{0}.pi'
        typo, sugg = 'my_imported_maths', 'my_imported_math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_imported(self):
        """Should be math.pi."""
        typo, sugg = 'pi', 'math.pi'
        self.code_throws(typo, ". Did you mean '" + sugg + "'\?")
        self.code_runs(sugg)

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

    def test_removed_reload(self):
        """Builtin reload is removed
        Moved to importlib.reload or imp.reload depending on version."""
        code = 'reload(math)'
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
        """Should be math.pi but module math is hidden."""
        code = 'math = ""\np = pi'
        self.code_throws(code, ". Did you mean 'math.pi' \(hidden\)\?")

    def test_self(self):
        self.code_throws(
            'FoobarClass().nameerror_self()', ". Did you mean 'self.bar'\?")

    def test_self2(self):
        sugg = "'[^ ]*.this_is_cls_mthd'"
        self.code_throws(
            'FoobarClass().nameerror_self2()',
            (". Did you mean " + sugg + ", " + sugg + "\?"))

    def test_cls(self):
        sugg = "'[^ ]*.this_is_cls_mthd'"
        self.code_throws(
            'FoobarClass().nameerror_cls()',
            (". Did you mean " + sugg + ", " + sugg + "\?"))


class UnboundLocalErrorTests(AbstractTests):
    """Class for tests related to UnboundLocalError."""
    error_type = UnboundLocalError
    error_msg = UNBOUNDERROR_RE

    def test_1(self):
        """Should be foo."""
        code = 'def func():\n\tfoo = 1\n\t{0} +=1\nfunc()'
        typo, sugg = "foob", "foo"
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)


class AttributeErrorTest(AbstractTests):
    """Class for tests related to AttributeError."""
    error_type = AttributeError
    error_msg = ATTRIBUTEERROR_RE

    def test_nonetype(self):
        """In-place methods like sort returns None.
        Might also happen if the functions misses a return."""
        code = '[].sort().append(4)'
        self.code_throws(code, "")

    def test_method(self):
        """Should be 'append'."""
        code = '[0].{0}(1)'
        typo, sugg = 'appendh', 'append'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_builtin(self):
        """Should be 'max(lst)'."""
        bad_code = '[0].max()'
        good_code = 'max([1])'
        self.code_throws(bad_code, ". Did you mean 'max\\(list\\)'\?")
        self.code_runs(good_code)

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
        """Should be 'lst.append(1)'."""
        code = '[0].{0}(1)'
        typo, sugg = 'add', 'append'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_wrongmethod2(self):
        """Should be 'lst.extend([4, 5, 6])'."""
        code = '[0].{0}([4, 5, 6])'
        typo, sugg = 'update', 'extend'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_hidden(self):
        """Accessing wrong string object."""
        # To be improved
        code = 'import string\nstring = "a"\nascii = string.ascii_letters'
        self.code_throws(code, "")

    def test_no_sugg(self):
        """No suggestion."""
        self.code_throws('[1, 2, 3].ldkjhfnvdlkjhvgfdhgf', "")

    def test_from_module(self):
        """Should be math.pi."""
        code = 'math.{0}'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_from_class(self):
        """Should be 'this_is_cls_mthd'."""
        code = 'FoobarClass().{0}()'
        typo, sugg = 'this_is_cls_mth', 'this_is_cls_mthd'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_from_class2(self):
        """Should be 'this_is_cls_mthd'."""
        code = 'FoobarClass.{0}()'
        typo, sugg = 'this_is_cls_mth', 'this_is_cls_mthd'
        bad_code, good_code = format_str(code, typo, sugg)
        # FIXME: self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

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
        """Method xreadlines is removed."""
        code = "import os\nwith open(os.path.realpath(__file__)) as f:" \
            "\n\tfor l in f.xreadlines():\n\t\tpass"
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))

    def test_removed_function_attributes(self):
        version = (3, 0)
        code = 'some_func.{0}'
        attributes = [('func_name', '__name__'),
                      ('func_doc', '__doc__'),
                      ('func_defaults', '__defaults__'),
                      ('func_dict', '__dict__'),
                      ('func_closure', '__closure__'),
                      ('func_globals', '__globals__'),
                      ('func_code', '__code__')]
        for (old_att, new_att) in attributes:
            old_code, new_code = format_str(code, old_att, new_att)
            self.code_runs(old_code, up_to_version(version))
            self.code_throws(old_code, "", from_version(version))
            self.code_runs(new_code)

    def test_removed_method_attributes(self):
        version = (3, 0)
        code = 'FoobarClass().some_method.{0}'
        attributes = [('im_func', '__func__'),
                      ('im_self', '__self__'),
                      ('im_class', '__self__.__class__')]
        for (old_att, new_att) in attributes:
            old_code, new_code = format_str(code, old_att, new_att)
            self.code_runs(old_code, up_to_version(version))
            self.code_throws(old_code, "", from_version(version))
            self.code_runs(new_code)


class TypeErrorTests(AbstractTests):
    """Class for tests related to TypeError."""
    error_type = TypeError


class TypeErrorMiscTests(TypeErrorTests):
    """Class for misc tests related to TypeError."""
    # TODO: Add sugg for situation where self/cls is the missing parameter

    def test_unhashable(self):
        self.code_throws('dict()[list()] = 1', "")


class TypeErrorTestsNotSub(TypeErrorTests):
    """Class for tests related to substriptable."""
    error_msg = UNSUBSCRIBTABLE_RE

    def test_not_sub(self):
        """Should be 'some_func(2)'."""
        self.code_throws(
            'some_func[2]', ". Did you mean 'function\\(value\\)'\?")


class TypeErrorTestsNumberArgs(TypeErrorTests):
    """Class for tests related to number of arguments."""

    def test_nb_args(self):
        """Should be 'some_func(1)'."""
        self.code_throws('some_func(1, 2)', "")


class TypeErrorTestsUnexpectedKwArg(TypeErrorTests):
    error_msg = UNEXPECTED_KEYWORDARG_RE

    def test_keyword_args(self):
        """Should be 'some_func(1)'."""
        code = 'some_func(a=1)'
        self.code_throws(code, "")

    def test_keyword_args2(self):
        """Should be 'some_func2(abcdef=1)'."""
        code = 'some_func2({0}=1)'
        typo, sugg = 'abcdf', 'abcdef'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)


class ImportErrorTests(AbstractTests):
    """Class for tests related to ImportError."""
    error_type = ImportError


class ImportErrorTestsNoModule(ImportErrorTests):
    """Class for tests related to no module."""
    error_msg = NOMODULE_RE

    def test_no_module_no_sugg(self):
        """No suggestion."""
        self.code_throws('import fqslkdfjslkqdjfqsd', "")

    def test_no_module(self):
        """Should be 'math'."""
        code = 'import {0}'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_no_module2(self):
        """Should be 'math'."""
        code = 'from {0} import pi'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_no_module3(self):
        """Should be 'math'."""
        code = 'import {0} as my_imported_math'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_no_module4(self):
        """Should be 'math'."""
        code = 'from {0} import pi as three_something'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)


class ImportErrorTestsCannotImport(ImportErrorTests):
    """Class for tests related to cannot import."""
    error_msg = CANNOTIMPORT_RE

    def test_no_name_no_sugg(self):
        """No suggestion."""
        self.code_throws('from math import fsfsdfdjlkf', "")

    def test_wrong_import(self):
        """Should be 'math'."""
        code = 'from {0} import pi'
        typo, sugg = 'itertools', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + good_code + "'\?")
        self.code_runs(good_code)

    def test_typo_in_method(self):
        """Should be 'pi'."""
        code = 'from math import {0}'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_typo_in_method2(self):
        """Should be 'pi'."""
        code = 'from math import e, {0}, log'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)

    def test_typo_in_method3(self):
        """Should be 'pi'."""
        code = 'from math import {0} as three_something'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.code_throws(bad_code, ". Did you mean '" + sugg + "'\?")
        self.code_runs(good_code)


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
    error_msg = INDEXOUTOFRANGE_RE

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
        code = 'print ""'
        new_code = 'print("")'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))
        self.code_runs(new_code)

    def test_exec(self):
        code = 'exec "1"'
        new_code = 'exec("1")'
        version = (3, 0)
        self.code_runs(code, up_to_version(version))
        self.code_throws(code, "", from_version(version))
        self.code_runs(new_code)

    def test_old_comparison(self):
        code = '1 {0} 2'
        old, new = '<>', '!='
        version = (3, 0)
        old_code, new_code = format_str(code, old, new)
        self.code_runs(old_code, up_to_version(version))
        self.code_throws(
            old_code,
            ". Did you mean '" + new + "'\?",
            from_version(version))
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

    def test_zero_len_field_in_format(self):
        code = '"{}".format(0)'
        version = (2, 7)
        self.code_throws(code, "", up_to_version(version))
        self.code_runs(code, from_version(version))


if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
