# -*- coding: utf-8
"""Unit tests for code in didyoumean.py."""
from didyoumean import get_suggestions_for_exception, get_suggestion_string
from didyoumean_re import UNBOUNDERROR_RE, NAMENOTDEFINED_RE,\
    ATTRIBUTEERROR_RE, UNSUBSCRIBTABLE_RE, UNEXPECTED_KEYWORDARG_RE,\
    NOMODULE_RE, CANNOTIMPORT_RE, INDEXOUTOFRANGE_RE, ZERO_LEN_FIELD_RE,\
    MATH_DOMAIN_ERROR_RE, TOO_MANY_VALUES_UNPACK_RE, OUTSIDE_FUNCTION_RE,\
    NEED_MORE_VALUES_RE, UNHASHABLE_RE, MISSING_PARENT_RE, INVALID_LITERAL_RE,\
    NB_ARG_RE, INVALID_SYNTAX_RE, EXPECTED_LENGTH_RE, INVALID_COMP_RE
from didyoumean_decorator import didyoumean
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
        self.babar = 2

    @classmethod
    def this_is_cls_mthd(cls):
        """Just a class method."""
        return 5

    def nameerror_self(self):
        """Should be self.babar."""
        return babar

    def nameerror_self2(self):
        """Should be self.this_is_cls_mthd (or FoobarClass)."""
        return this_is_cls_mthd

    @classmethod
    def nameerror_cls(cls):
        """Should be cls.this_is_cls_mthd (or FoobarClass)."""
        return this_is_cls_mthd

    def some_method(self):
        pass


def some_func(babar):
    """Dummy function for testing purposes."""
    return babar


def some_func2(abcdef=None):
    """Dummy function for testing purposes."""
    return abcdef


def some_func3():
    pass


def some_func4(so, much, args):
    pass

# Logic to be able to have different tests on various version of Python
FIRST_VERSION = (0, 0)
LAST_VERSION = (10, 0)
ALL_VERSIONS = (FIRST_VERSION, LAST_VERSION)
is_pypy = hasattr(sys, "pypy_translation_info")


def from_version(version):
    """Create tuple describing a range of versions from a given version."""
    return (version, LAST_VERSION)


def up_to_version(version):
    """Create tuple describing a range of versions up to a given version."""
    return (FIRST_VERSION, version)


def format_str(template, *args):
    """Format multiple string by using first arg as a template."""
    return [template.format(arg) for arg in args]


def version_in_range(version_range):
    beg, end = version_range
    return beg <= sys.version_info < end


# Tests
class AbstractTests(unittest2.TestCase):
    """Generic class to test get_suggestions_for_exception."""

    def no_exception(self, code):
        """Helper function to run code and check it works."""
        exec(code)

    def get_exception(self, code):
        """Helper function to run code and get what it throws."""
        try:
            exec(code)
        except:
            return sys.exc_info()
        self.assertTrue(False)

    def runs(self, code, version_range=ALL_VERSIONS):
        """Helper function to run code."""
        if version_in_range(version_range):
            self.no_exception(code)

    def throws(self, code, error_info,
               sugg=None, version_range=ALL_VERSIONS):
        """Helper function to run code and check what it throws
        that what we have expected suggestions."""
        if version_in_range(version_range):
            error_type, error_msg = error_info
            type_caught, value, traceback = self.get_exception(code)
            self.assertTrue(issubclass(error_type, type_caught))
            if error_msg is not None:
                self.assertRegexpMatches(''.join(value.args[0]), error_msg)
            if sugg is None:
                sugg = []
            if not isinstance(sugg, list):
                sugg = [sugg]
            suggestions = sorted(
                get_suggestions_for_exception(
                    type_caught, value, traceback))
            self.assertEqual(suggestions, sugg)


# NameError
NAMEERROR = (NameError, NAMENOTDEFINED_RE)
UNKNOWN_NAMEERROR = (NameError, None)
# UnboundLocalError
UNBOUNDLOCAL = (UnboundLocalError, UNBOUNDERROR_RE)
UNKNOWN_UNBOUNDLOCAL = (UnboundLocalError, None)
# TypeError
NBARGERROR = (TypeError, NB_ARG_RE)
UNHASHABLE = (TypeError, UNHASHABLE_RE)
UNSUBSCRIBTABLE = (TypeError, UNSUBSCRIBTABLE_RE)
UNEXPECTEDKWARG = (TypeError, UNEXPECTED_KEYWORDARG_RE)
# ImportError
NOMODULE = (ImportError, NOMODULE_RE)
CANNOTIMPORT = (ImportError, CANNOTIMPORT_RE)
UNKNOWN_IMPORTERROR = (ImportError, None)
# KeyError
KEYERROR = (KeyError, None)
# IndexError
OUTOFRANGE = (IndexError, INDEXOUTOFRANGE_RE)
# ValueError
TOOMANYVALUES = (ValueError, TOO_MANY_VALUES_UNPACK_RE)
NEEDMOREVALUES = (ValueError, NEED_MORE_VALUES_RE)
EXPECTEDLENGTH = (ValueError, EXPECTED_LENGTH_RE)
MATHDOMAIN = (ValueError, MATH_DOMAIN_ERROR_RE)
ZEROLENERROR = (ValueError, ZERO_LEN_FIELD_RE)
INVALIDLITERAL = (ValueError, INVALID_LITERAL_RE)
# AttributeError
ATTRIBUTEERROR = (AttributeError, ATTRIBUTEERROR_RE)
UNKNOWN_ATTRIBUTEERROR = (AttributeError, None)
# SyntaxError
INVALIDSYNTAX = (SyntaxError, INVALID_SYNTAX_RE)
OUTSIDEFUNC = (SyntaxError, OUTSIDE_FUNCTION_RE)
MISSINGPARENT = (SyntaxError, MISSING_PARENT_RE)
INVALIDCOMP = (SyntaxError, INVALID_COMP_RE)


class NameErrorTests(AbstractTests):
    """Class for tests related to NameError."""

    def test_local(self):
        """Should be 'foo'."""
        code = "foo = 0\n{0}"
        typo, sugg = "foob", "foo"
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NAMEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_1_arg(self):
        """Should be 'foo'."""
        code = "def func(foo):\n\t{0}\nfunc(1)"
        typo, sugg = "foob", "foo"
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NAMEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_n_args(self):
        """Should be 'fool' or 'foot'."""
        code = "def func(fool, foot, bar):\n\t{0}\nfunc(1, 2, 3)"
        typo, sugg1, sugg2 = "foob", "foot", "fool"
        bad, good1, good2 = format_str(code, typo, sugg1, sugg2)
        self.throws(bad, NAMEERROR, ["'fool'", "'foot'"])
        self.runs(good1)
        self.runs(good2)

    def test_builtin(self):
        """Should be 'max'."""
        typo, sugg = 'maxi', 'max'
        self.throws(typo, NAMEERROR, "'" + sugg + "'")
        self.runs(sugg)

    def test_keyword(self):
        """Should be 'pass'."""
        typo, sugg = 'passs', 'pass'
        self.throws(typo, NAMEERROR, "'" + sugg + "'")
        self.runs(sugg)

    def test_global(self):
        """Should be this_is_a_global_list."""
        typo, sugg = 'this_is_a_global_lis', 'this_is_a_global_list'
        self.throws(typo, NAMEERROR, "'" + sugg + "'")
        self.runs(sugg)

    def test_import(self):
        """Should be math.pi."""
        code = 'import math\n{0}.pi'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NAMEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_import2(self):
        """Should be my_imported_math.pi."""
        code = 'import math as my_imported_math\n{0}.pi'
        typo, sugg = 'my_imported_maths', 'my_imported_math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NAMEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_imported(self):
        """Should be math.pi."""
        code = 'import math\n{0}'
        typo, sugg = 'pi', 'math.pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NAMEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_imported_twice(self):
        """Should be math.pi."""
        code = 'import math\nimport math\n{0}'
        typo, sugg = 'pi', 'math.pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NAMEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_no_sugg(self):
        """No suggestion."""
        self.throws('a = ldkjhfnvdlkjhvgfdhgf', NAMEERROR)

    def test_removed_cmp(self):
        """Builtin cmp is removed."""
        code = 'cmp(1, 2)'
        version = (3, 0, 1)
        self.runs(code, up_to_version(version))
        self.throws(code, NAMEERROR, [], from_version(version))

    def test_removed_reduce(self):
        """Builtin reduce is removed - moved to functools."""
        code = 'reduce(lambda x, y: x + y, [1, 2, 3, 4, 5])'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, NAMEERROR, [], from_version(version))

    def test_removed_apply(self):
        """Builtin apply is removed."""
        code = 'apply(sum, [[1, 2, 3]])'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, NAMEERROR, [], from_version(version))

    def test_removed_reload(self):
        """Builtin reload is removed
        Moved to importlib.reload or imp.reload depending on version."""
        code = 'reload(math)'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, NAMEERROR, [], from_version(version))

    def test_removed_intern(self):
        """Builtin intern is removed - moved to sys."""
        code = 'intern("toto")'
        new_code = 'sys.intern("toto")'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(
            code, NAMEERROR,
            ["'iter'", "'sys.intern'"],
            from_version(version))
        self.runs(new_code, from_version(version))

    def test_removed_execfile(self):
        """Builtin execfile is removed - use exec() and compile()."""
        code = 'execfile("some_filename")'
        version = (3, 0)
        # self.runs(code, up_to_version(version))
        self.throws(code, NAMEERROR, [], from_version(version))

    def test_removed_raw_input(self):
        """Builtin raw_input is removed - use input() instead."""
        code = 'i = raw_input("Prompt:")'
        version = (3, 0)
        # self.runs(code, up_to_version(version))
        self.throws(code, NAMEERROR, "'input'", from_version(version))

    def test_removed_buffer(self):
        """Builtin buffer is removed - use memoryview instead."""
        code = 'buffer("abc")'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, NAMEERROR, [], from_version(version))

    def test_import_sugg(self):
        """Should import functools first."""
        sugg = ['to import functools first']
        # re.functools is sometimes suggested :-/
        if version_in_range(((3, 2), (3, 4))):
            sugg.insert(0, "'re.functools'")
        self.throws('w = functools.wraps', NAMEERROR, sugg)

    def test_attribute_hidden(self):
        """Should be math.pi but module math is hidden."""
        math.pi  # just a way to say that math module is needed in globals
        code = 'math = ""\np = pi'
        self.throws(code, NAMEERROR, "'math.pi' (hidden)")

    def test_self(self):
        """"Should be self.babar."""
        self.throws(
            'FoobarClass().nameerror_self()',
            NAMEERROR, ["'self.babar'"])

    def test_self2(self):
        """Should be self.this_is_cls_mthd."""
        self.throws(
            'FoobarClass().nameerror_self2()', NAMEERROR,
            ["'FoobarClass.this_is_cls_mthd'", "'self.this_is_cls_mthd'"])

    def test_cls(self):
        """Should be cls.this_is_cls_mthd."""
        self.throws(
            'FoobarClass().nameerror_cls()', NAMEERROR,
            ["'FoobarClass.this_is_cls_mthd'", "'cls.this_is_cls_mthd'"])

    def test_unmatched_msg(self):
        """Test that arbitrary strings are supported."""
        self.throws(
            'raise NameError("unmatched NAMEERROR")',
            UNKNOWN_NAMEERROR)


class UnboundLocalErrorTests(AbstractTests):
    """Class for tests related to UnboundLocalError."""

    def test_1(self):
        """Should be foo."""
        code = 'def func():\n\tfoo = 1\n\t{0} +=1\nfunc()'
        typo, sugg = "foob", "foo"
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, UNBOUNDLOCAL, "'" + sugg + "'")
        self.runs(good_code)

    def test_unmatched_msg(self):
        """Test that arbitrary strings are supported."""
        self.throws(
            'raise UnboundLocalError("unmatched UNBOUNDLOCAL")',
            UNKNOWN_UNBOUNDLOCAL)


class AttributeErrorTest(AbstractTests):
    """Class for tests related to AttributeError."""

    def test_nonetype(self):
        """In-place methods like sort returns None.
        Might also happen if the functions misses a return."""
        code = '[].sort().append(4)'
        self.throws(code, ATTRIBUTEERROR)

    def test_method(self):
        """Should be 'append'."""
        code = '[0].{0}(1)'
        typo, sugg = 'appendh', 'append'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, ATTRIBUTEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_builtin(self):
        """Should be 'max(lst)'."""
        bad_code, good_code = '[0].max()', 'max([0])'
        self.throws(bad_code, ATTRIBUTEERROR, "'max(list)'")
        self.runs(good_code)

    def test_builtin2(self):
        """Should be 'next(gen)'."""
        code = 'my_generator().next()'
        new_code = 'next(my_generator())'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(
            code, ATTRIBUTEERROR,
            "'next(generator)'",
            from_version(version))
        self.runs(new_code)

    def test_wrongmethod(self):
        """Should be 'lst.append(1)'."""
        code = '[0].{0}(1)'
        typo, sugg = 'add', 'append'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, ATTRIBUTEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_wrongmethod2(self):
        """Should be 'lst.extend([4, 5, 6])'."""
        code = '[0].{0}([4, 5, 6])'
        typo, sugg = 'update', 'extend'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, ATTRIBUTEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_hidden(self):
        """Accessing wrong string object."""
        # To be improved
        code = 'import string\nstring = "a"\nascii = string.ascii_letters'
        self.throws(code, ATTRIBUTEERROR)

    def test_no_sugg(self):
        """No suggestion."""
        self.throws('[1, 2, 3].ldkjhfnvdlkjhvgfdhgf', ATTRIBUTEERROR)

    def test_from_module(self):
        """Should be math.pi."""
        code = 'import math\nmath.{0}'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, ATTRIBUTEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_from_class(self):
        """Should be 'this_is_cls_mthd'."""
        code = 'FoobarClass().{0}()'
        typo, sugg = 'this_is_cls_mth', 'this_is_cls_mthd'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, ATTRIBUTEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_from_class2(self):
        """Should be 'this_is_cls_mthd'."""
        code = 'FoobarClass.{0}()'
        typo, sugg = 'this_is_cls_mth', 'this_is_cls_mthd'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, ATTRIBUTEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_removed_has_key(self):
        """Method has_key is removed from dict."""
        code = 'dict().has_key(1)'
        new_code = '1 in dict()'
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(
            code,
            ATTRIBUTEERROR,
            "'key in dict'", from_version(version))
        self.runs(new_code)

    def test_removed_xreadlines(self):
        """Method xreadlines is removed."""
        code = "import os\nwith open(os.path.realpath(__file__)) as f:" \
            "\n\tfor l in f.xreadlines():\n\t\tpass"
        version = (3, 0)
        self.runs(code, up_to_version(version))
        self.throws(code, ATTRIBUTEERROR, [], from_version(version))

    def test_removed_function_attributes(self):
        """Some functions attributes are removed."""
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
            self.throws(old_code, ATTRIBUTEERROR, [], from_version(version))
            self.runs(new_code)

    def test_removed_method_attributes(self):
        """Some methods attributes are removed."""
        version = (3, 0)
        version = (3, 0)
        code = 'FoobarClass().some_method.{0}'
        attributes = [('im_func', '__func__'),
                      ('im_self', '__self__'),
                      ('im_class', '__self__.__class__')]
        for (old_att, new_att) in attributes:
            old_code, new_code = format_str(code, old_att, new_att)
            self.runs(old_code, up_to_version(version))
            self.throws(old_code, ATTRIBUTEERROR, [], from_version(version))
            self.runs(new_code)

    def test_unmatched_msg(self):
        """Test that arbitrary strings are supported."""
        self.throws(
            'raise AttributeError("unmatched ATTRIBUTEERROR")',
            UNKNOWN_ATTRIBUTEERROR)

    # TODO: Add sugg for situation where self/cls is the missing parameter
    def test_unhashable(self):
        """Test that other errors do not crash."""
        self.throws('dict()[list()] = 1', UNHASHABLE)

    def test_not_sub(self):
        """Should be 'some_func(2)'."""
        self.throws('some_func[2]', UNSUBSCRIBTABLE, "'function(value)'")

    def test_nb_args(self):
        """Should be 'some_func(1)'."""
        self.throws('some_func(1, 2)', NBARGERROR)

    def test_nb_args2(self):
        """Should be 'some_func3()'."""
        self.throws('some_func3(1)', NBARGERROR)

    def test_nb_args3(self):
        """Should be 'some_func4(1, 2, 3)'."""
        pass
        # FIXME self.throws('some_func4(1)', NBARGERROR)

    def test_nb_args4(self):
        """Should be 'some_func4(1, 2, 3)'."""
        pass
        # FIXME self.throws('some_func4()', NBARGERROR)

    def test_keyword_args(self):
        """Should be 'some_func(1)'."""
        code = 'some_func(a=1)'
        self.throws(code, UNEXPECTEDKWARG)

    def test_keyword_args2(self):
        """Should be 'some_func2(abcdef=1)'."""
        code = 'some_func2({0}=1)'
        typo, sugg = 'abcdf', 'abcdef'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, UNEXPECTEDKWARG, "'" + sugg + "'")
        self.runs(good_code)


class ImportErrorTests(AbstractTests):
    """Class for tests related to ImportError."""

    def test_no_module_no_sugg(self):
        """No suggestion."""
        self.throws('import fqslkdfjslkqdjfqsd', NOMODULE)

    def test_no_module(self):
        """Should be 'math'."""
        code = 'import {0}'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NOMODULE, "'" + sugg + "'")
        self.runs(good_code)

    def test_no_module2(self):
        """Should be 'math'."""
        code = 'from {0} import pi'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NOMODULE, "'" + sugg + "'")
        self.runs(good_code)

    def test_no_module3(self):
        """Should be 'math'."""
        code = 'import {0} as my_imported_math'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NOMODULE, "'" + sugg + "'")
        self.runs(good_code)

    def test_no_module4(self):
        """Should be 'math'."""
        code = 'from {0} import pi as three_something'
        typo, sugg = 'maths', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NOMODULE, "'" + sugg + "'")
        self.runs(good_code)

    def test_no_name_no_sugg(self):
        """No suggestion."""
        self.throws('from math import fsfsdfdjlkf', CANNOTIMPORT)

    def test_wrong_import(self):
        """Should be 'math'."""
        code = 'from {0} import pi'
        typo, sugg = 'itertools', 'math'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, CANNOTIMPORT, "'" + good_code + "'")
        self.runs(good_code)

    def test_typo_in_method(self):
        """Should be 'pi'."""
        code = 'from math import {0}'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, CANNOTIMPORT, "'" + sugg + "'")
        self.runs(good_code)

    def test_typo_in_method2(self):
        """Should be 'pi'."""
        code = 'from math import e, {0}, log'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, CANNOTIMPORT, "'" + sugg + "'")
        self.runs(good_code)

    def test_typo_in_method3(self):
        """Should be 'pi'."""
        code = 'from math import {0} as three_something'
        typo, sugg = 'pie', 'pi'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, CANNOTIMPORT, "'" + sugg + "'")
        self.runs(good_code)

    def test_unmatched_msg(self):
        """Test that arbitrary strings are supported."""
        self.throws(
            'raise ImportError("unmatched IMPORTERROR")',
            UNKNOWN_IMPORTERROR)


class LookupErrorTests(AbstractTests):
    """Class for tests related to LookupError."""


class KeyErrorTests(LookupErrorTests):
    """Class for tests related to KeyError."""

    def test_no_sugg(self):
        """No suggestion."""
        self.throws('dict()["ffdsqmjklfqsd"]', KEYERROR)


class IndexErrorTests(LookupErrorTests):
    """Class for tests related to IndexError."""

    def test_no_sugg(self):
        """No suggestion."""
        self.throws('list()[2]', OUTOFRANGE)


class SyntaxErrorTests(AbstractTests):
    """Class for tests related to SyntaxError."""

    def test_no_error(self):
        self.runs("1 + 2 == 2")

    def test_yield_return_out_of_func(self):
        sugg = "to indent it"
        self.throws("yield 1", OUTSIDEFUNC, sugg)
        self.throws("return 1", OUTSIDEFUNC, ["sys.exit([arg])", sugg])

    def test_print(self):
        code, new_code = 'print ""', 'print("")'
        version = (3, 0)
        version2 = (3, 4)
        self.runs(code, up_to_version(version))
        self.throws(code, INVALIDSYNTAX, [], (version, version2))
        self.throws(code, INVALIDSYNTAX, [], from_version(version2))
        self.runs(new_code)

    def test_exec(self):
        code, new_code = 'exec "1"', 'exec("1")'
        version = (3, 0)
        version2 = (3, 4)
        self.runs(code, up_to_version(version))
        self.throws(code, INVALIDSYNTAX, [], (version, version2))
        self.throws(code, INVALIDSYNTAX, [], from_version(version2))
        self.runs(new_code)

    def test_old_comparison(self):
        code = '1 {0} 2'
        old, new = '<>', '!='
        version = (3, 0)
        old_code, new_code = format_str(code, old, new)
        self.runs(old_code, up_to_version(version))
        self.throws(
            old_code,
            INVALIDCOMP if is_pypy else INVALIDSYNTAX,
            "'!='", from_version(version))
        self.runs(new_code)


class ValueErrorTests(AbstractTests):
    """Class for tests related to ValueError."""

    def test_too_many_values(self):
        code = 'a, b, c = [1, 2, 3, 4]'
        if is_pypy:
            version = (3, 0)
            self.throws(code, EXPECTEDLENGTH, [], up_to_version(version))
            self.throws(code, TOOMANYVALUES, [], from_version(version))
        else:
            self.throws(code, TOOMANYVALUES)

    def test_not_enough_values(self):
        code = 'a, b, c = [1, 2]'
        if is_pypy:
            version = (3, 0)
            self.throws(code, EXPECTEDLENGTH, [], up_to_version(version))
            self.throws(code, NEEDMOREVALUES, [], from_version(version))
        else:
            self.throws(code, NEEDMOREVALUES)

    def test_conversion_fails(self):
        self.throws('int("toto")', INVALIDLITERAL)

    def test_math_domain(self):
        code = 'import math\nlg = math.log(-1)'
        self.throws(code, MATHDOMAIN)

    def test_zero_len_field_in_format(self):
        code = '"{}".format(0)'
        version = (2, 7)
        self.throws(code, ZEROLENERROR, [], up_to_version(version))
        self.runs(code, from_version(version))


class RegexTests(unittest2.TestCase):
    """Tests to check that error messages match the regexps."""

    def regex_matches(self, text, regexp, groups=None):
        """Check that text matches regexp giving groups given values."""
        self.assertRegexpMatches(text, regexp)   # does pretty printing
        m = re.match(regexp, text)
        self.assertTrue(m)
        self.assertEqual(groups, m.groups())

    def test_unbound_assignment(self):
        """ Test UNBOUNDERROR_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        s = "local variable 'some_var' referenced before assignment"
        self.regex_matches(s, UNBOUNDERROR_RE, ('some_var',))

    def test_name_not_defined(self):
        """ Test NAMENOTDEFINED_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy3
        s1 = "name 'some_name' is not defined"
        # Python 2.6/2.7/3.2/3.3/PyPy/PyPy3
        s2 = "global name 'some_name' is not defined"
        groups = ('some_name',)
        self.regex_matches(s1, NAMENOTDEFINED_RE, groups)
        self.regex_matches(s2, NAMENOTDEFINED_RE, groups)

    def test_attribute_error(self):
        """ Test ATTRIBUTEERROR_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        s1 = "'some.class' object has no attribute 'attri'"
        g1 = ('some.class', 'attri')
        # Python 2.6/2.7/PyPy
        s2 = "SomeClass instance has no attribute 'attri'"
        g2 = ('SomeClass', 'attri')
        # Python 3.5
        s3 = "module 'some_module' has no attribute 'attri'"
        g3 = ('some_module', 'attri')
        # Python 2.6/2.7
        s4 = "class SomeClass has no attribute 'attri'"
        # Python 3.2/3.3/3.4/3.5
        s5 = "type object 'SomeClass' has no attribute 'attri'"
        self.regex_matches(s1, ATTRIBUTEERROR_RE, g1)
        self.regex_matches(s2, ATTRIBUTEERROR_RE, g2)
        self.regex_matches(s3, ATTRIBUTEERROR_RE, g3)
        self.regex_matches(s4, ATTRIBUTEERROR_RE, g2)
        self.regex_matches(s5, ATTRIBUTEERROR_RE, g2)

    def test_cannot_import(self):
        """ Test CANNOTIMPORT_RE ."""
        # Python 2.6/2.7/3.2/3.3
        s1 = "cannot import name pie"
        # Python 3.4/3.5/PyPy/PyPy3
        s2 = "cannot import name 'pie'"
        groups = ('pie',)
        self.regex_matches(s1, CANNOTIMPORT_RE, groups)
        self.regex_matches(s2, CANNOTIMPORT_RE, groups)

    def test_no_module_named(self):
        """ Test NOMODULE_RE ."""
        # Python 2.6/2.7/3.2/PyPy/PyPy3
        s1 = "No module named fake_module"
        # Python 3.3/3.4/3.5
        s2 = "No module named 'fake_module'"
        groups = ('fake_module', )
        self.regex_matches(s1, NOMODULE_RE, groups)
        self.regex_matches(s2, NOMODULE_RE, groups)

    def test_index_out_of_range(self):
        """ Test INDEXOUTOFRANGE_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        s = "list index out of range"
        self.regex_matches(s, INDEXOUTOFRANGE_RE, ())

    def test_unsubscriptable(self):
        """ Test UNSUBSCRIBTABLE_RE ."""
        # Python 2.6
        s1 = "'function' object is unsubscriptable"
        # Python 2.7
        s2 = "'function' object has no attribute '__getitem__'"
        # Python 3.2/3.3/3.4/3.5/PyPy/PyPy3
        s3 = "'function' object is not subscriptable"
        groups = ('function',)
        self.regex_matches(s1, UNSUBSCRIBTABLE_RE, groups)
        self.regex_matches(s2, UNSUBSCRIBTABLE_RE, groups)
        self.regex_matches(s3, UNSUBSCRIBTABLE_RE, groups)

    def test_unexpected_kw_arg(self):
        """ Test UNEXPECTED_KEYWORDARG_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        s = "some_func() got an unexpected keyword argument 'a'"
        self.regex_matches(s, UNEXPECTED_KEYWORDARG_RE, ('some_func', 'a'))

    def test_zero_length_field(self):
        """ Test ZERO_LEN_FIELD_RE ."""
        # Python 2.6
        s = "zero length field name in format"
        self.regex_matches(s, ZERO_LEN_FIELD_RE, ())

    def test_math_domain_error(self):
        """ Test MATH_DOMAIN_ERROR_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        s = "math domain error"
        self.regex_matches(s, MATH_DOMAIN_ERROR_RE, ())

    def test_too_many_values(self):
        """ Test TOO_MANY_VALUES_UNPACK_RE ."""
        # Python 2.6/2.7
        s1 = "too many values to unpack"
        # Python 3.2/3.3/3.4/3.5/PyPy3
        s2 = "too many values to unpack (expected 3)"
        self.regex_matches(s1, TOO_MANY_VALUES_UNPACK_RE, ())
        self.regex_matches(s2, TOO_MANY_VALUES_UNPACK_RE, ())

    def test_unhashable_type(self):
        """ Test UNHASHABLE_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5
        s1 = "unhashable type: 'list'"
        # PyPy/PyPy3
        s2 = "'list' objects are unhashable"
        self.regex_matches(s1, UNHASHABLE_RE, ('list',))
        self.regex_matches(s2, UNHASHABLE_RE, ('list',))

    def test_outside_function(self):
        """ Test OUTSIDE_FUNCTION_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        s1 = "'return' outside function"
        # PyPy/PyPy3
        s2 = "return outside function"
        self.regex_matches(s1, OUTSIDE_FUNCTION_RE, ('return',))
        self.regex_matches(s2, OUTSIDE_FUNCTION_RE, ('return',))

    def test_nb_positional_argument(self):
        """ Test NB_ARG_RE ."""
        # Python 2.6/2.7
        s1 = "some_func() takes exactly 1 argument (2 given)"
        # Python 3.2/PyPy/PyPy3
        s2 = "some_func() takes exactly 1 positional argument (2 given)"
        # Python 3.3/3.4/3.5
        s3 = "some_func() takes 1 positional argument but 2 were given"
        # Various versions - TBD
        s4 = "some_func() takes no arguments (1 given)"
        s5 = "some_func() takes exactly 3 arguments (1 given)"
        s6 = "some_func() takes 0 positional arguments but 1 was given"
        # FIXME
        s7 = "some_func() missing 2 required positional arguments: " \
            "'much' and 'args'"
        groups = ('some_func',)
        for s in (s1, s2, s3, s4, s5, s6):
            self.regex_matches(s, NB_ARG_RE, groups)

    def test_need_more_values_to_unpack(self):
        """ Test NEED_MORE_VALUES_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy3
        s = "need more than 2 values to unpack"
        self.regex_matches(s, NEED_MORE_VALUES_RE, ())

    def test_missing_parentheses(self):
        """ Test MISSING_PARENT_RE ."""
        # Python 3.4/3.5
        s = "Missing parentheses in call to 'exec'"
        self.regex_matches(s, MISSING_PARENT_RE, ('exec',))

    def test_invalid_literal(self):
        """ Test INVALID_LITERAL_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        s = "invalid literal for int() with base 10: 'toto'"
        self.regex_matches(s, INVALID_LITERAL_RE, ('int', 'toto'))

    def test_invalid_syntax(self):
        """ Test INVALID_SYNTAX_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy3
        s = "invalid syntax"
        self.regex_matches(s, INVALID_SYNTAX_RE, ())

    def test_invalid_comp(self):
        """ Test INVALID_COMP_RE ."""
        # PyPy3
        s = "invalid comparison"
        self.regex_matches(s, INVALID_COMP_RE, ())

    def test_expected_length(self):
        """ Test EXPECTED_LENGTH_RE ."""
        # PyPy
        s = "expected length 3, got 2"
        self.regex_matches(s, EXPECTED_LENGTH_RE, ('3', '2'))


class GetSuggStringTests(unittest2.TestCase):
    """ Tests about get_suggestion_string. """

    def test_no_sugg(self):
        """ Empty list of suggestions. """
        self.assertEqual(get_suggestion_string(()), "")

    def test_one_sugg(self):
        """ Single suggestion. """
        self.assertEqual(get_suggestion_string(()), "")
        self.assertEqual(get_suggestion_string(('0',)), ". Did you mean 0?")

    def test_same_sugg(self):
        """ Identical suggestion. """
        self.assertEqual(
            get_suggestion_string(('0', '0')), ". Did you mean 0, 0?")

    def test_multiple_suggs(self):
        """ Multiple suggestions. """
        self.assertEqual(
            get_suggestion_string(('0', '1')), ". Did you mean 0, 1?")


class DecoratorTest(AbstractTests):
    """ Tests about the didyoumean decorator. """

    def func_1(self, babar):
        return babar

    def func_2(self, babar):
        return baba

    def func_3(self, babar):
        return gdfsdfsdfsdfsd

    @didyoumean
    def func_1_deco(self, babar):
        return babar

    @didyoumean
    def func_2_deco(self, babar):
        return baba

    @didyoumean
    def func_3_deco(self, babar):
        return gdfsdfsdfsdfsd

    def test_decorator_no_exception(self):
        """Check the case with no exception."""
        self.no_exception('self.func_1(0)')
        self.no_exception('self.func_1_deco(0)')

    def test_decorator_suggestion(self):
        """Check the case with a suggestion."""
        sugg = ". Did you mean 'babar'?"
        type1, value1, _ = self.get_exception('self.func_2(0)')
        type2, value2, _ = self.get_exception('self.func_2_deco(0)')
        self.assertEqual(type1, NameError)
        self.assertEqual(type2, NameError)
        self.assertEqual(str(value1) + sugg, str(value2))

    def test_decorator_no_suggestion(self):
        """Check the case with no suggestion."""
        type1, value1, _ = self.get_exception('self.func_3(0)')
        type2, value2, _ = self.get_exception('self.func_3_deco(0)')
        self.assertEqual(type1, NameError)
        self.assertEqual(type2, NameError)
        self.assertEqual(str(value1), str(value2))

if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
