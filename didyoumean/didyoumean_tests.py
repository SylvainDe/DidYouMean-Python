# -*- coding: utf-8
"""Unit tests for code in didyoumean.py."""
from didyoumean_decorator import didyoumean
from didyoumean_re import UNBOUNDERROR_RE, NAMENOTDEFINED_RE,\
    ATTRIBUTEERROR_RE, UNSUBSCRIBTABLE_RE, UNEXPECTED_KEYWORDARG_RE,\
    NOMODULE_RE, CANNOTIMPORT_RE, INDEXOUTOFRANGE_RE, ZERO_LEN_FIELD_RE,\
    MATH_DOMAIN_ERROR_RE, TOO_MANY_VALUES_UNPACK_RE, OUTSIDE_FUNCTION_RE,\
    NEED_MORE_VALUES_RE, UNHASHABLE_RE, MISSING_PARENT_RE, INVALID_LITERAL_RE,\
    NB_ARG_RE
import unittest2
import math
import sys
import re

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

    def runs(self, code, version_range=ALL_VERSIONS):
        """Helper function to run code and check it works."""
        beg, end = version_range
        if beg <= sys.version_info < end:
            exec_wrapper(code)
            exec_wrapper_deco(code)

    def throws(self, code, error_info, sugg, version_range=ALL_VERSIONS):
        """Helper function to run code and check it throws."""
        beg, end = version_range
        if beg <= sys.version_info < end:
            error_type, error_msg = error_info
            trunc = error_msg[:-1] if error_msg.endswith('$') else error_msg
            error_msg_with_sugg = trunc + sugg + "$"
            self.my_assert_raises_rexp(
                error_type,
                error_msg,
                exec_wrapper,
                code)
            self.my_assert_raises_rexp(
                error_type,
                error_msg_with_sugg,
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


# NameError
nameerror = (NameError, NAMENOTDEFINED_RE)
# UnboundLocalError
unbounderror = (UnboundLocalError, UNBOUNDERROR_RE)
# TypeError
nbargerror = (TypeError, NB_ARG_RE)
unhashableerror = (TypeError, UNHASHABLE_RE)
notsubscriberror = (TypeError, UNSUBSCRIBTABLE_RE)
unexpectedkwerror = (TypeError, UNEXPECTED_KEYWORDARG_RE)
# ImportError
nomoduleerror = (ImportError, NOMODULE_RE)
cannotimport = (ImportError, CANNOTIMPORT_RE)
# KeyError
keyerror = (KeyError, "")
# IndexError
outofrangeerror = (IndexError, INDEXOUTOFRANGE_RE)
# ValueError
toomanyvalueserror = (ValueError, TOO_MANY_VALUES_UNPACK_RE)
needmorevalues = (ValueError, NEED_MORE_VALUES_RE)
mathdomainerror = (ValueError, MATH_DOMAIN_ERROR_RE)
zerolenerror = (ValueError, ZERO_LEN_FIELD_RE)
invalidliteral = (ValueError, INVALID_LITERAL_RE)
# AttributeError
attributeerror = (AttributeError, ATTRIBUTEERROR_RE)
# SyntaxError
syntaxerror = (SyntaxError, "")  # "^invalid syntax$"
outsidefunctionerror = (SyntaxError, OUTSIDE_FUNCTION_RE)
missingparent = (SyntaxError, MISSING_PARENT_RE)


class NameErrorTests(AbstractTests):
    """Class for tests related to NameError."""

    def test_local(self):
        """Should be 'foo'."""
        code = "foo = 0\n{0}"
        typo, sugg = "foob", "foo"
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, nameerror, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_1_arg(self):
        """Should be 'foo'."""
        code = "def func(foo):\n\t{0}\nfunc(1)"
        typo, sugg = "foob", "foo"
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, nameerror, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_n_args(self):
        """Should be 'fool' or 'foot'."""
        code = "def func(fool, foot, bar):\n\t{0}\nfunc(1, 2, 3)"
        typo, sugg1, sugg2 = "foob", "foot", "fool"
        bad, good1, good2 = format_str(code, typo, sugg1, sugg2)
        self.throws(bad, nameerror, ". Did you mean 'foot', 'fool'\?")
        self.runs(good1)
        self.runs(good2)

    def test_builtin(self):
        """Should be 'max'."""
        typo, sugg = 'maxi', 'max'
        self.throws(typo, nameerror, ". Did you mean '" + sugg + "'\?")
        self.runs(sugg)

    def test_keyword(self):
        """Should be 'pass'."""
        typo, sugg = 'passs', 'pass'
        self.throws(typo, nameerror, ". Did you mean '" + sugg + "'\?")
        self.runs(sugg)

    def test_global(self):
        """Should be this_is_a_global_list."""
        typo, sugg = 'this_is_a_global_lis', 'this_is_a_global_list'
        self.throws(typo, nameerror, ". Did you mean '" + sugg + "'\?")
        self.runs(sugg)

    def test_import(self):
        """Should be math.pi."""
        code = '{0}.pi'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, nameerror, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_import2(self):
        """Should be my_imported_math.pi."""
        code = 'import math as my_imported_math\n{0}.pi'
        typo, sugg = 'my_imported_maths', 'my_imported_math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, nameerror, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_imported(self):
        """Should be math.pi."""
        typo, sugg = 'pi', 'math.pi'
        self.throws(typo, nameerror, ". Did you mean '" + sugg + "'\?")
        self.runs(sugg)

    def test_no_sugg(self):
        """No suggestion."""
        self.throws('a = ldkjhfnvdlkjhvgfdhgf', nameerror, "")

    def test_removed_cmp(self):
        """Builtin cmp is removed."""
        code = 'cmp(1, 2)'
        version = (3, 0, 1)
        self.runs(code, up_to_version(version))
        self.throws(code, nameerror, "", from_version(version))

    def test_removed_reduce(self):
        """Builtin reduce is removed - moved to functools."""
        code = 'reduce(lambda x, y: x + y, [1, 2, 3, 4, 5])'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, nameerror, "", from_version(version))

    def test_removed_apply(self):
        """Builtin apply is removed."""
        code = 'apply(sum, [[1, 2, 3]])'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, nameerror, "", from_version(version))

    def test_removed_reload(self):
        """Builtin reload is removed
        Moved to importlib.reload or imp.reload depending on version."""
        code = 'reload(math)'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, nameerror, "", from_version(version))

    def test_removed_intern(self):
        """Builtin intern is removed - moved to sys."""
        code = 'intern("toto")'
        new_code = 'sys.intern("toto")'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(
            code, nameerror,
            ". Did you mean 'sys.intern', 'iter'\?",
            from_version(version))
        self.runs(new_code, from_version(version))

    def test_removed_execfile(self):
        """Builtin execfile is removed - use exec() and compile()."""
        code = 'execfile("some_filename")'
        version = (3, 0)
        # self.runs(code, up_to_version(version))
        self.throws(code, nameerror, "", from_version(version))

    def test_removed_raw_input(self):
        """Builtin raw_input is removed - use input() instead."""
        code = 'i = raw_input("Prompt:")'
        version = (3, 0)
        # self.runs(code, up_to_version(version))
        self.throws(
            code, nameerror,
            ". Did you mean 'input'\?",
            from_version(version))

    def test_removed_buffer(self):
        """Builtin buffer is removed - use memoryview instead."""
        code = 'buffer("abc")'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, nameerror, "", from_version(version))

    def test_import_sugg(self):
        """Should import functools first."""
        self.throws(
            'w = functools.wraps', nameerror,
            ". Did you mean ('re.functools', )?to import functools first\?")

    def test_attribute_hidden(self):
        """Should be math.pi but module math is hidden."""
        code = 'math = ""\np = pi'
        self.throws(code, nameerror, ". Did you mean 'math.pi' \(hidden\)\?")

    def test_self(self):
        self.throws(
            'FoobarClass().nameerror_self()',
            nameerror,
            ". Did you mean 'self.bar'\?")

    def test_self2(self):
        sugg = "'[^ ]*.this_is_cls_mthd'"
        self.throws(
            'FoobarClass().nameerror_self2()', nameerror,
            (". Did you mean " + sugg + ", " + sugg + "\?"))

    def test_cls(self):
        sugg = "'[^ ]*.this_is_cls_mthd'"
        self.throws(
            'FoobarClass().nameerror_cls()', nameerror,
            (". Did you mean " + sugg + ", " + sugg + "\?"))


class UnboundLocalErrorTests(AbstractTests):
    """Class for tests related to UnboundLocalError."""

    def test_1(self):
        """Should be foo."""
        code = 'def func():\n\tfoo = 1\n\t{0} +=1\nfunc()'
        typo, sugg = "foob", "foo"
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, unbounderror, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)


class AttributeErrorTest(AbstractTests):
    """Class for tests related to AttributeError."""

    def test_nonetype(self):
        """In-place methods like sort returns None.
        Might also happen if the functions misses a return."""
        code = '[].sort().append(4)'
        self.throws(code, attributeerror, "")

    def test_method(self):
        """Should be 'append'."""
        code = '[0].{0}(1)'
        typo, sugg = 'appendh', 'append'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(
            bad_code,
            attributeerror,
            ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_builtin(self):
        """Should be 'max(lst)'."""
        bad_code = '[0].max()'
        good_code = 'max([1])'
        self.throws(
            bad_code,
            attributeerror,
            ". Did you mean 'max\\(list\\)'\?")
        self.runs(good_code)

    def test_builtin2(self):
        """Should be 'next(gen)'."""
        code = 'my_generator().next()'
        new_code = 'next(my_generator())'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(
            code, attributeerror,
            ". Did you mean 'next\\(generator\\)'\?",
            from_version(version))
        self.runs(new_code)

    def test_wrongmethod(self):
        """Should be 'lst.append(1)'."""
        code = '[0].{0}(1)'
        typo, sugg = 'add', 'append'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(
            bad_code,
            attributeerror,
            ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_wrongmethod2(self):
        """Should be 'lst.extend([4, 5, 6])'."""
        code = '[0].{0}([4, 5, 6])'
        typo, sugg = 'update', 'extend'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(
            bad_code,
            attributeerror,
            ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_hidden(self):
        """Accessing wrong string object."""
        # To be improved
        code = 'import string\nstring = "a"\nascii = string.ascii_letters'
        self.throws(code, attributeerror, "")

    def test_no_sugg(self):
        """No suggestion."""
        self.throws('[1, 2, 3].ldkjhfnvdlkjhvgfdhgf', attributeerror, "")

    def test_from_module(self):
        """Should be math.pi."""
        code = 'math.{0}'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(
            bad_code,
            attributeerror,
            ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_from_class(self):
        """Should be 'this_is_cls_mthd'."""
        code = 'FoobarClass().{0}()'
        typo, sugg = 'this_is_cls_mth', 'this_is_cls_mthd'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(
            bad_code,
            attributeerror,
            ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_from_class2(self):
        """Should be 'this_is_cls_mthd'."""
        code = 'FoobarClass.{0}()'
        typo, sugg = 'this_is_cls_mth', 'this_is_cls_mthd'
        bad_code, good_code = format_str(code, typo, sugg)
        # FIXME
        # self.throws(
        #     bad_code,
        #     attributeerror,
        #     ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_removed_has_key(self):
        """Method has_key is removed from dict."""
        code = 'dict().has_key(1)'
        new_code = '1 in dict()'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(
            code,
            attributeerror,
            ". Did you mean 'key in dict'\?", from_version(version))
        self.runs(new_code)

    def test_removed_xreadlines(self):
        """Method xreadlines is removed."""
        code = "import os\nwith open(os.path.realpath(__file__)) as f:" \
            "\n\tfor l in f.xreadlines():\n\t\tpass"
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, attributeerror, "", from_version(version))

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
            self.runs(old_code, up_to_version(version))
            self.throws(old_code, attributeerror, "", from_version(version))
            self.runs(new_code)

    def test_removed_method_attributes(self):
        version = (3, 0)
        code = 'FoobarClass().some_method.{0}'
        attributes = [('im_func', '__func__'),
                      ('im_self', '__self__'),
                      ('im_class', '__self__.__class__')]
        for (old_att, new_att) in attributes:
            old_code, new_code = format_str(code, old_att, new_att)
            self.runs(old_code, up_to_version(version))
            self.throws(old_code, attributeerror, "", from_version(version))
            self.runs(new_code)

    # TODO: Add sugg for situation where self/cls is the missing parameter
    def test_unhashable(self):
        self.throws('dict()[list()] = 1', unhashableerror, "")

    def test_not_sub(self):
        """Should be 'some_func(2)'."""
        self.throws(
            'some_func[2]',
            notsubscriberror,
            ". Did you mean 'function\\(value\\)'\?")

    def test_nb_args(self):
        """Should be 'some_func(1)'."""
        self.throws('some_func(1, 2)', nbargerror, "")

    def test_keyword_args(self):
        """Should be 'some_func(1)'."""
        code = 'some_func(a=1)'
        self.throws(code, unexpectedkwerror, "")

    def test_keyword_args2(self):
        """Should be 'some_func2(abcdef=1)'."""
        code = 'some_func2({0}=1)'
        typo, sugg = 'abcdf', 'abcdef'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(
            bad_code,
            unexpectedkwerror,
            ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)


class ImportErrorTests(AbstractTests):
    """Class for tests related to ImportError."""

    def test_no_module_no_sugg(self):
        """No suggestion."""
        self.throws('import fqslkdfjslkqdjfqsd', nomoduleerror, "")

    def test_no_module(self):
        """Should be 'math'."""
        code = 'import {0}'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, nomoduleerror, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_no_module2(self):
        """Should be 'math'."""
        code = 'from {0} import pi'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, nomoduleerror, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_no_module3(self):
        """Should be 'math'."""
        code = 'import {0} as my_imported_math'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, nomoduleerror, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_no_module4(self):
        """Should be 'math'."""
        code = 'from {0} import pi as three_something'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, nomoduleerror, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_no_name_no_sugg(self):
        """No suggestion."""
        self.throws('from math import fsfsdfdjlkf', cannotimport, "")

    def test_wrong_import(self):
        """Should be 'math'."""
        code = 'from {0} import pi'
        typo, sugg = 'itertools', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(
            bad_code,
            cannotimport,
            ". Did you mean '" + good_code + "'\?")
        self.runs(good_code)

    def test_typo_in_method(self):
        """Should be 'pi'."""
        code = 'from math import {0}'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, cannotimport, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_typo_in_method2(self):
        """Should be 'pi'."""
        code = 'from math import e, {0}, log'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, cannotimport, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)

    def test_typo_in_method3(self):
        """Should be 'pi'."""
        code = 'from math import {0} as three_something'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, cannotimport, ". Did you mean '" + sugg + "'\?")
        self.runs(good_code)


class LookupErrorTests(AbstractTests):
    """Class for tests related to LookupError."""


class KeyErrorTests(LookupErrorTests):
    """Class for tests related to KeyError."""

    def test_no_sugg(self):
        """No suggestion."""
        self.throws('dict()["ffdsqmjklfqsd"]', keyerror, "")


class IndexErrorTests(LookupErrorTests):
    """Class for tests related to IndexError."""

    def test_no_sugg(self):
        """No suggestion."""
        self.throws('list()[2]', outofrangeerror, "")


class SyntaxErrorTests(AbstractTests):
    """Class for tests related to SyntaxError."""

    def test_no_error(self):
        self.runs("1 + 2 == 2")

    def test_yield_return_out_of_func(self):
        self.throws("yield 1", outsidefunctionerror, "")
        self.throws("return 1", outsidefunctionerror, "")

    def test_print(self):
        code, new_code = 'print ""', 'print("")'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, syntaxerror, "", from_version(version))
        self.runs(new_code)

    def test_exec(self):
        code, new_code = 'exec "1"', 'exec("1")'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, syntaxerror, "", from_version(version))
        self.runs(new_code)

    def test_old_comparison(self):
        code = '1 {0} 2'
        old, new = '<>', '!='
        version = (3, 0)
        old_code, new_code = format_str(code, old, new)
        self.runs(old_code, up_to_version(version))
        self.throws(
            old_code,
            syntaxerror,
            ". Did you mean '" + new + "'\?",
            from_version(version))
        self.runs(new_code)


class ValueErrorTests(AbstractTests):
    """Class for tests related to ValueError."""

    def test_too_many_values(self):
        self.throws('a, b, c = [1, 2, 3, 4]', toomanyvalueserror, "")

    def test_not_enough_values(self):
        self.throws('a, b, c = [1, 2]', needmorevalues, "")

    def test_conversion_fails(self):
        self.throws('int("toto")', invalidliteral, "")

    def test_math_domain(self):
        self.throws('lg = math.log(-1)', mathdomainerror, "")

    def test_zero_len_field_in_format(self):
        code = '"{}".format(0)'
        version = (2, 7)
        self.throws(code, zerolenerror, "", up_to_version(version))
        self.runs(code, from_version(version))


class RegexTests(unittest2.TestCase):
    """Tests to check that eror messages match the regexps."""

    def regexMatches(self, text, regexp, groups=None):
        """Check that text matches regexp giving groups given values."""
        self.assertRegexpMatches(text, regexp)   # does pretty printing
        m = re.match(regexp, text)
        assert(m)
        assert(groups == m.groups())

    def test_unbound_assignment(self):
        # Python 2.6/2.7/3.2/3.3/3.4
        s = "local variable 'some_var' referenced before assignment"
        self.regexMatches(s, UNBOUNDERROR_RE, ('some_var',))

    def test_name_not_defined(self):
        # Python 2.6/2.7/3.2/3.3/3.4
        s1 = "name 'some_name' is not defined"
        # Python 2.6/2.7/3.2/3.3
        s2 = "global name 'some_name' is not defined"
        groups = ('some_name',)
        self.regexMatches(s1, NAMENOTDEFINED_RE, groups)
        self.regexMatches(s2, NAMENOTDEFINED_RE, groups)

    def test_attribute_error(self):
        # Python 2.6/2.7/3.2/3.3/3.4
        s1 = "'some.class' object has no attribute 'attri'"
        g1 = ('some.class', 'attri')
        # Python 2.6/2.7
        s2 = "SomeClass instance has no attribute 'attri'"
        g2 = ('SomeClass', 'attri')
        self.regexMatches(s1, ATTRIBUTEERROR_RE, g1)
        self.regexMatches(s2, ATTRIBUTEERROR_RE, g2)

    def test_cannot_import(self):
        # Python 2.6/2.7/3.2/3.3
        s1 = "cannot import name pie"
        # Python 3.4
        s2 = "cannot import name 'pie'"
        groups = ('pie',)
        self.regexMatches(s1, CANNOTIMPORT_RE, groups)
        self.regexMatches(s2, CANNOTIMPORT_RE, groups)

    def test_no_module_named(self):
        # Python 2.6/2.7/3.2
        s1 = "No module named fake_module"
        # Python 3.3/3.4
        s2 = "No module named 'fake_module'"
        groups = ('fake_module', )
        self.regexMatches(s1, NOMODULE_RE, groups)
        self.regexMatches(s2, NOMODULE_RE, groups)

    def test_index_out_of_range(self):
        # Python 2.6/2.7/3.2/3.3/3.4
        s = "list index out of range"
        self.regexMatches(s, INDEXOUTOFRANGE_RE, ())

    def test_unsubscriptable(self):
        # Python 2.6
        s1 = "'function' object is unsubscriptable"
        # Python 2.7
        s2 = "'function' object has no attribute '__getitem__'"
        # Python 3.2/3.3/3.4
        s3 = "'function' object is not subscriptable"
        groups = ('function',)
        self.regexMatches(s1, UNSUBSCRIBTABLE_RE, groups)
        self.regexMatches(s2, UNSUBSCRIBTABLE_RE, groups)
        self.regexMatches(s3, UNSUBSCRIBTABLE_RE, groups)

    def test_unexpected_kw_arg(self):
        # Python 2.6/2.7/3.2/3.3/3.4
        s = "some_func() got an unexpected keyword argument 'a'"
        self.regexMatches(s, UNEXPECTED_KEYWORDARG_RE, ('some_func', 'a'))

    def test_zero_length_field(self):
        # Python 2.6
        s = "zero length field name in format"
        self.regexMatches(s, ZERO_LEN_FIELD_RE, ())

    def test_math_domain_error(self):
        # Python 2.6/2.7/3.2/3.3/3.4
        s = "math domain error"
        self.regexMatches(s, MATH_DOMAIN_ERROR_RE, ())

    def test_too_many_values(self):
        # Python 2.6/2.7
        s1 = "too many values to unpack"
        # Python 3.2/3.3/3.4
        s2 = "too many values to unpack (expected 3)"
        self.regexMatches(s1, TOO_MANY_VALUES_UNPACK_RE, ())
        self.regexMatches(s2, TOO_MANY_VALUES_UNPACK_RE, ())

    def test_unhashable_type(self):
        # Python 2.6/2.7/3.2/3.3/3.4
        s = "unhashable type: 'list'"
        self.regexMatches(s, UNHASHABLE_RE, ('list',))

    def test_outside_function(self):
        # Python 2.6/2.7/3.2/3.3/3.4
        s = "'return' outside function"
        self.regexMatches(s, OUTSIDE_FUNCTION_RE, ('return',))

    def test_nb_positional_argument(self):
        # Python 2.6/2.7
        s1 = "some_func() takes exactly 1 argument (2 given)"
        # Python 3.2
        s2 = "some_func() takes exactly 1 positional argument (2 given)"
        # Python 3.3/3.4
        s3 = "some_func() takes 1 positional argument but 2 were given"
        groups = ('some_func',)
        self.regexMatches(s1, NB_ARG_RE, groups)
        self.regexMatches(s2, NB_ARG_RE, groups)
        self.regexMatches(s3, NB_ARG_RE, groups)

    def test_need_more_values_to_unpack(self):
        # Python 2.6/2.7/3.2/3.3/3.4
        s = "need more than 2 values to unpack"
        self.regexMatches(s, NEED_MORE_VALUES_RE, ())

    def test_missing_parentheses(self):
        # Python 3.4
        s = "Missing parentheses in call to 'exec'"
        self.regexMatches(s, MISSING_PARENT_RE, ('exec',))

    def test_invalid_literal(self):
        # Python 2.6/2.7/3.2/3.3/3.4
        s = "invalid literal for int() with base 10: 'toto'"
        self.regexMatches(s, INVALID_LITERAL_RE, ('int', 'toto'))

if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
