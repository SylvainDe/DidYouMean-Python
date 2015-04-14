# -*- coding: utf-8
"""Unit tests for code in didyoumean.py."""
from didyoumean import get_suggestions_for_exception, get_suggestion_string,\
    add_string_to_exception
from didyoumean_re import UNBOUNDERROR_RE, NAMENOTDEFINED_RE,\
    ATTRIBUTEERROR_RE, UNSUBSCRIBTABLE_RE, UNEXPECTED_KEYWORDARG_RE,\
    NOMODULE_RE, CANNOTIMPORT_RE, INDEXOUTOFRANGE_RE, ZERO_LEN_FIELD_RE,\
    MATH_DOMAIN_ERROR_RE, TOO_MANY_VALUES_UNPACK_RE, OUTSIDE_FUNCTION_RE,\
    NEED_MORE_VALUES_RE, UNHASHABLE_RE, MISSING_PARENT_RE, INVALID_LITERAL_RE,\
    NB_ARG_RE, INVALID_SYNTAX_RE, EXPECTED_LENGTH_RE, INVALID_COMP_RE,\
    MISSING_POS_ARG_RE, FUTURE_FIRST_RE, FUTURE_FEATURE_NOT_DEF_RE
from didyoumean_decorator import didyoumean
import unittest2
import math
import sys
import re

# Following code is bad on purpose - please do not fix ;-)

this_is_a_global_list = [1, 2]


def func_gen(name='some_func', param='', body='pass', args=None):
    """Function to generate code for function def (and sometimes a call to it).
    Parameters are : name (with default), body (with default),
    parameters (with default) and arguments to call the functions with (if not
    provided or provided None, function call is not included in generated
    code."""
    func = "def {0}({1}):\n\t{2}\n".format(name, param, body)
    call = "" if args is None else "{0}({1})\n".format(name, args)
    return func + call


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
        """Method for testing purposes."""
        pass


# Logic to be able to have different tests on various version of Python
FIRST_VERSION = (0, 0)
LAST_VERSION = (10, 0)
ALL_VERSIONS = (FIRST_VERSION, LAST_VERSION)
IS_PYPY = hasattr(sys, "pypy_translation_info")


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
    """ Check that version is in a range version."""
    beg, end = version_range
    return beg <= sys.version_info < end


def no_exception(code):
    """Helper function to run code and check it works."""
    exec(code)


def get_exception(code):
    """Helper function to run code and get what it throws."""
    try:
        exec(code)
    except:
        return sys.exc_info()
    assert False, "No exception thrown"


# Tests
class AbstractTests(unittest2.TestCase):
    """Generic class to test get_suggestions_for_exception."""

    def runs(self, code, version_range=ALL_VERSIONS):
        """Helper function to run code."""
        if version_in_range(version_range):
            no_exception(code)

    def throws(self, code, error_info,
               sugg=None, version_range=ALL_VERSIONS):
        """Helper function to run code and check what it throws
        that what we have expected suggestions."""
        if version_in_range(version_range):
            error_type, error_msg = error_info
            type_caught, value, traceback = get_exception(code)
            self.assertTrue(
                issubclass(error_type, type_caught),
                "%s not a subclass of %s" % (error_type, type_caught))
            if error_msg is not None:
                self.assertRegexpMatches(value.args[0], error_msg)
            if sugg is None:
                sugg = []
            if not isinstance(sugg, list):
                sugg = [sugg]
            suggestions = sorted(
                get_suggestions_for_exception(
                    type_caught, value, traceback))
            self.assertEqual(suggestions, sugg)


# NameError for NameErrorTests
NAMEERROR = (NameError, NAMENOTDEFINED_RE)
UNKNOWN_NAMEERROR = (NameError, None)
# UnboundLocalError for UnboundLocalErrorTests
UNBOUNDLOCAL = (UnboundLocalError, UNBOUNDERROR_RE)
UNKNOWN_UNBOUNDLOCAL = (UnboundLocalError, None)
# TypeError for TypeErrorTests
NBARGERROR = (TypeError, NB_ARG_RE)
MISSINGPOSERROR = (TypeError, MISSING_POS_ARG_RE)
UNHASHABLE = (TypeError, UNHASHABLE_RE)
UNSUBSCRIBTABLE = (TypeError, UNSUBSCRIBTABLE_RE)
UNEXPECTEDKWARG = (TypeError, UNEXPECTED_KEYWORDARG_RE)
UNKNOWN_TYPEERROR = (TypeError, None)
# ImportError for ImportErrorTests
NOMODULE = (ImportError, NOMODULE_RE)
CANNOTIMPORT = (ImportError, CANNOTIMPORT_RE)
UNKNOWN_IMPORTERROR = (ImportError, None)
# KeyError for KeyErrorTests
KEYERROR = (KeyError, None)
# IndexError for IndexErrorTests
OUTOFRANGE = (IndexError, INDEXOUTOFRANGE_RE)
# ValueError for ValueErrorTests
TOOMANYVALUES = (ValueError, TOO_MANY_VALUES_UNPACK_RE)
NEEDMOREVALUES = (ValueError, NEED_MORE_VALUES_RE)
EXPECTEDLENGTH = (ValueError, EXPECTED_LENGTH_RE)
MATHDOMAIN = (ValueError, MATH_DOMAIN_ERROR_RE)
ZEROLENERROR = (ValueError, ZERO_LEN_FIELD_RE)
INVALIDLITERAL = (ValueError, INVALID_LITERAL_RE)
# AttributeError for AttributeErrorTests
ATTRIBUTEERROR = (AttributeError, ATTRIBUTEERROR_RE)
UNKNOWN_ATTRIBUTEERROR = (AttributeError, None)
# SyntaxError for SyntaxErrorTests
INVALIDSYNTAX = (SyntaxError, INVALID_SYNTAX_RE)
OUTSIDEFUNC = (SyntaxError, OUTSIDE_FUNCTION_RE)
MISSINGPARENT = (SyntaxError, MISSING_PARENT_RE)
INVALIDCOMP = (SyntaxError, INVALID_COMP_RE)
FUTUREFIRST = (SyntaxError, FUTURE_FIRST_RE)
FUTFEATNOTDEF = (SyntaxError, FUTURE_FEATURE_NOT_DEF_RE)


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
        typo, sugg = "foob", "foo"
        code = func_gen(param=sugg, body='{0}', args='1')
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NAMEERROR, "'" + sugg + "'")
        self.runs(good_code)

    def test_n_args(self):
        """Should be 'fool' or 'foot'."""
        typo, sugg1, sugg2 = "foob", "foot", "fool"
        code = func_gen(param='fool, foot', body='{0}', args='1, 2')
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
            NAMEERROR, "'self.babar'")

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

    def test_main(self):
        """Should be '__main__'."""
        self.throws('__main_', NAMEERROR)

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


class AttributeErrorTests(AbstractTests):
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
        code = func_gen() + 'some_func.{0}'
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

    def test_join(self):
        """This can be frustrating, a suggestion could be nice."""
        code = "['a', 'b'].join('-')"
        self.throws(code, ATTRIBUTEERROR)

    def test_unmatched_msg(self):
        """Test that arbitrary strings are supported."""
        self.throws(
            'raise AttributeError("unmatched ATTRIBUTEERROR")',
            UNKNOWN_ATTRIBUTEERROR)

    # TODO: Add sugg for situation where self/cls is the missing parameter


class TypeErrorTests(AbstractTests):
    """Class for tests related to TypeError."""

    def test_unhashable(self):
        """Test that other errors do not crash."""
        self.throws('dict()[list()] = 1', UNHASHABLE)

    def test_not_sub(self):
        """Should be function call, not [] operator."""
        typo, sugg = '[2]', '(2)'
        code = func_gen(param='a') + 'some_func{0}'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, UNSUBSCRIBTABLE, "'function(value)'")
        self.runs(good_code)

    def test_nb_args(self):
        """Should have 1 arg."""
        typo, sugg = '1, 2', '1'
        code = func_gen(param='a', args='{0}')
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, NBARGERROR)
        self.runs(good_code)

    def test_nb_args1(self):
        """Should have 0 args."""
        typo, sugg = '1', ''
        code = func_gen(param='', args='{0}')
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, UNKNOWN_TYPEERROR)  # FIXME
        self.runs(good_code)

    def test_nb_args2(self):
        """Should have 1 arg."""
        typo, sugg = '', '1'
        code = func_gen(param='a', args='{0}')
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, UNKNOWN_TYPEERROR)  # FIXME
        self.runs(good_code)

    def test_nb_args3(self):
        """Should have 3 args."""
        typo, sugg = '1', '1, 2, 3'
        code = func_gen(param='so, much, args', args='{0}')
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, UNKNOWN_TYPEERROR)  # FIXME
        self.runs(good_code)

    def test_nb_args4(self):
        """Should have 3 args."""
        typo, sugg = '', '1, 2, 3'
        code = func_gen(param='so, much, args', args='{0}')
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, UNKNOWN_TYPEERROR)  # FIXME
        self.runs(good_code)

    def test_nb_args5(self):
        """Should have 3 args."""
        typo, sugg = '1, 2', '1, 2, 3'
        code = func_gen(param='so, much, args', args='{0}')
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, UNKNOWN_TYPEERROR)  # FIXME
        self.runs(good_code)

    def test_keyword_args(self):
        """Should be param 'babar' not 'a' but it's hard to guess."""
        typo, sugg = 'a', 'babar'
        code = func_gen(param=sugg, args='{0}=1')
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, UNEXPECTEDKWARG)
        self.runs(good_code)

    def test_keyword_args2(self):
        """Should be param 'abcdef' not 'abcdf'."""
        typo, sugg = 'abcdf', 'abcdef'
        code = func_gen(param=sugg, args='{0}=1')
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, UNEXPECTEDKWARG, "'" + sugg + "'")
        self.runs(good_code)

    def test_no_implicit_str_conv(self):
        """ Trying to concatenate a non-string value to a string."""
        pass

    def test_assignment_to_range(self):
        """ Trying to assign to range works on list, not on range."""
        # FIXME
        code = '{0}[2] = 1'
        typo, sugg = 'range(4)', 'list(range(4))'
        version = (3, 0)
        bad_code, good_code = format_str(code, typo, sugg)
        self.runs(bad_code, up_to_version(version))
        self.throws(bad_code, UNKNOWN_TYPEERROR, [], from_version(version))
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

    def test_import_future_nomodule(self):
        """ Should be '__future__' ."""
        code = 'import {0}'
        typo, sugg = '__future_', '__future__'
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
        """ No error."""
        self.runs("1 + 2 == 2")

    def test_yield_return_out_of_func(self):
        """ yield/return needs to be in functions."""
        sugg = "to indent it"
        self.throws("yield 1", OUTSIDEFUNC, sugg)
        self.throws("return 1", OUTSIDEFUNC, ["'sys.exit([arg])'", sugg])

    def test_print(self):
        """ print is a functions now and needs parenthesis."""
        code, new_code = 'print ""', 'print("")'
        version = (3, 0)
        version2 = (3, 4)
        self.runs(code, up_to_version(version))
        self.throws(code, INVALIDSYNTAX, [], (version, version2))
        self.throws(code, INVALIDSYNTAX, [], from_version(version2))
        self.runs(new_code)

    def test_exec(self):
        """ exec is a functions now and needs parenthesis."""
        code, new_code = 'exec "1"', 'exec("1")'
        version = (3, 0)
        version2 = (3, 4)
        self.runs(code, up_to_version(version))
        self.throws(code, INVALIDSYNTAX, [], (version, version2))
        self.throws(code, INVALIDSYNTAX, [], from_version(version2))
        self.runs(new_code)

    def test_old_comparison(self):
        """ <> comparison is removed, != always works."""
        code = '1 {0} 2'
        old, new = '<>', '!='
        version = (3, 0)
        old_code, new_code = format_str(code, old, new)
        self.runs(old_code, up_to_version(version))
        self.throws(
            old_code,
            INVALIDCOMP if IS_PYPY else INVALIDSYNTAX,
            "'!='", from_version(version))
        self.runs(new_code)

    def test_missing_colon(self):
        """ Missing colon is a classic mistake."""
        code = "if True{0}\n\tpass"
        bad_code, good_code = format_str(code, "", ":")
        self.throws(bad_code, INVALIDSYNTAX)
        self.runs(good_code)

    def test_simple_equal(self):
        """ '=' for comparison is a classic mistake."""
        code = "if 2 {0} 3:\n\tpass"
        bad_code, good_code = format_str(code, "=", "==")
        self.throws(bad_code, INVALIDSYNTAX)
        self.runs(good_code)

    def test_keyword_as_identifier(self):
        """ Using a keyword as a variable name. """
        code = '{0} = 1'
        bad_code, good_code = format_str(code, "from", "from_")
        self.throws(bad_code, INVALIDSYNTAX)
        self.runs(good_code)

    def test_increment(self):
        """ Using a keyword as a variable name. """
        code = 'a = 0\na{0}'
        for op in ('-', '+'):
            typo, sugg = 2*op, op + '=1'
            bad_code, good_code = format_str(code, typo, sugg)
            self.throws(bad_code, INVALIDSYNTAX)
            self.runs(good_code)

    def test_import_future_not_first(self):
        """ Imports from __future__ need before anything else ."""
        code = 'a = 8/7\nfrom __future__ import division'
        self.throws(code, FUTUREFIRST)

    def test_import_future_not_def(self):
        """ Should be 'division' ."""
        code = 'from __future__ import {0}'
        typo, sugg = 'divisio', 'division'
        bad_code, good_code = format_str(code, typo, sugg)
        self.throws(bad_code, FUTFEATNOTDEF, "'" + sugg + "'")
        self.runs(good_code)


class ValueErrorTests(AbstractTests):
    """Class for tests related to ValueError."""

    def test_too_many_values(self):
        """ Unpack 4 values in 3 variables."""
        code = 'a, b, c = [1, 2, 3, 4]'
        if IS_PYPY:
            version = (3, 0)
            self.throws(code, EXPECTEDLENGTH, [], up_to_version(version))
            self.throws(code, TOOMANYVALUES, [], from_version(version))
        else:
            self.throws(code, TOOMANYVALUES)

    def test_not_enough_values(self):
        """ Unpack 2 values in 3 variables."""
        code = 'a, b, c = [1, 2]'
        if IS_PYPY:
            version = (3, 0)
            self.throws(code, EXPECTEDLENGTH, [], up_to_version(version))
            self.throws(code, NEEDMOREVALUES, [], from_version(version))
        else:
            self.throws(code, NEEDMOREVALUES)

    def test_conversion_fails(self):
        """ Conversion fails."""
        self.throws('int("toto")', INVALIDLITERAL)

    def test_math_domain(self):
        """ Math function used out of its domain."""
        code = 'import math\nlg = math.log(-1)'
        self.throws(code, MATHDOMAIN)

    def test_zero_len_field_in_format(self):
        """ Format {} is not valid before Python 2.7."""
        code = '"{}".format(0)'
        version = (2, 7)
        self.throws(code, ZEROLENERROR, [], up_to_version(version))
        self.runs(code, from_version(version))


class RegexTests(unittest2.TestCase):
    """Tests to check that error messages match the regexps."""

    def regex_matches(self, text, regexp, groups=None):
        """Check that text matches regexp giving groups given values."""
        self.assertRegexpMatches(text, regexp)   # does pretty printing
        match = re.match(regexp, text)
        self.assertTrue(match)
        self.assertEqual(groups, match.groups())

    def test_unbound_assignment(self):
        """ Test UNBOUNDERROR_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "local variable 'some_var' referenced before assignment"
        self.regex_matches(msg, UNBOUNDERROR_RE, ('some_var',))

    def test_name_not_defined(self):
        """ Test NAMENOTDEFINED_RE ."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy3
            "name 'some_name' is not defined",
            # Python 2.6/2.7/3.2/3.3/PyPy/PyPy3
            "global name 'some_name' is not defined",
        ]
        groups = ('some_name',)
        for msg in msgs:
            self.regex_matches(msg, NAMENOTDEFINED_RE, groups)

    def test_attribute_error(self):
        """ Test ATTRIBUTEERROR_RE ."""
        group_msg = {
            ('some.class', 'attri'): [
                # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
                "'some.class' object has no attribute 'attri'",
            ],
            ('SomeClass', 'attri'): [
                # Python 2.6/2.7/PyPy
                "SomeClass instance has no attribute 'attri'",
                # Python 2.6/2.7
                "class SomeClass has no attribute 'attri'",
                # Python 3.2/3.3/3.4/3.5
                "type object 'SomeClass' has no attribute 'attri'",
            ],
            ('some_module', 'attri'): [
                # Python 3.5
                "module 'some_module' has no attribute 'attri'",
            ]
        }
        for group, msgs in group_msg.items():
            for msg in msgs:
                self.regex_matches(msg, ATTRIBUTEERROR_RE, group)

    def test_cannot_import(self):
        """ Test CANNOTIMPORT_RE ."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3
            "cannot import name pie",
            # Python 3.4/3.5/PyPy/PyPy3
            "cannot import name 'pie'",
        ]
        groups = ('pie',)
        for msg in msgs:
            self.regex_matches(msg, CANNOTIMPORT_RE, groups)

    def test_no_module_named(self):
        """ Test NOMODULE_RE ."""
        msgs = [
            # Python 2.6/2.7/3.2/PyPy/PyPy3
            "No module named fake_module",
            # Python 3.3/3.4/3.5
            "No module named 'fake_module'",
        ]
        groups = ('fake_module', )
        for msg in msgs:
            self.regex_matches(msg, NOMODULE_RE, groups)

    def test_index_out_of_range(self):
        """ Test INDEXOUTOFRANGE_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "list index out of range"
        self.regex_matches(msg, INDEXOUTOFRANGE_RE, ())

    def test_unsubscriptable(self):
        """ Test UNSUBSCRIBTABLE_RE ."""
        msgs = [
            # Python 2.6
            "'function' object is unsubscriptable",
            # Python 2.7
            "'function' object has no attribute '__getitem__'",
            # Python 3.2/3.3/3.4/3.5/PyPy/PyPy3
            "'function' object is not subscriptable",
        ]
        groups = ('function',)
        for msg in msgs:
            self.regex_matches(msg, UNSUBSCRIBTABLE_RE, groups)

    def test_unexpected_kw_arg(self):
        """ Test UNEXPECTED_KEYWORDARG_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "some_func() got an unexpected keyword argument 'a'"
        self.regex_matches(msg, UNEXPECTED_KEYWORDARG_RE, ('some_func', 'a'))

    def test_zero_length_field(self):
        """ Test ZERO_LEN_FIELD_RE ."""
        # Python 2.6
        msg = "zero length field name in format"
        self.regex_matches(msg, ZERO_LEN_FIELD_RE, ())

    def test_math_domain_error(self):
        """ Test MATH_DOMAIN_ERROR_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "math domain error"
        self.regex_matches(msg, MATH_DOMAIN_ERROR_RE, ())

    def test_too_many_values(self):
        """ Test TOO_MANY_VALUES_UNPACK_RE ."""
        msgs = [
            # Python 2.6/2.7
            "too many values to unpack",
            # Python 3.2/3.3/3.4/3.5/PyPy3
            "too many values to unpack (expected 3)",
        ]
        for msg in msgs:
            self.regex_matches(msg, TOO_MANY_VALUES_UNPACK_RE, ())

    def test_unhashable_type(self):
        """ Test UNHASHABLE_RE ."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5
            "unhashable type: 'list'",
            # PyPy/PyPy3
            "'list' objects are unhashable",
        ]
        for msg in msgs:
            self.regex_matches(msg, UNHASHABLE_RE, ('list',))

    def test_outside_function(self):
        """ Test OUTSIDE_FUNCTION_RE ."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
            "'return' outside function",
            # PyPy/PyPy3
            "return outside function",
        ]
        for msg in msgs:
            self.regex_matches(msg, OUTSIDE_FUNCTION_RE, ('return',))

    def test_nb_positional_argument(self):
        """ Test NB_ARG_RE ."""
        msgs = [
            # Python 2.6/2.7/PyPy/PyPy3
            "some_func() takes exactly 1 argument (2 given)",
            "some_func() takes exactly 3 arguments (1 given)",
            "some_func() takes no arguments (1 given)",
            # Python 3.2
            "some_func() takes exactly 1 positional argument (2 given)",
            # Python 3.3/3.4/3.5
            "some_func() takes 1 positional argument but 2 were given",
            "some_func() takes 0 positional arguments but 1 was given",
        ]
        groups = ('some_func',)
        for msg in msgs:
            self.regex_matches(msg, NB_ARG_RE, groups)

    def test_missing_positional_arg(self):
        """ Test MISSING_POS_ARG_RE ."""
        msgs = [
            # Python 3.3/3.4/3.5
            "some_func() missing 2 required positional arguments: "
            "'much' and 'args'",
            "some_func() missing 1 required positional argument: "
            "'much'",
        ]
        groups = ('some_func',)
        for msg in msgs:
            self.regex_matches(msg, MISSING_POS_ARG_RE, groups)

    def test_need_more_values_to_unpack(self):
        """ Test NEED_MORE_VALUES_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy3
        msg = "need more than 2 values to unpack"
        self.regex_matches(msg, NEED_MORE_VALUES_RE, ())

    def test_missing_parentheses(self):
        """ Test MISSING_PARENT_RE ."""
        # Python 3.4/3.5
        msg = "Missing parentheses in call to 'exec'"
        self.regex_matches(msg, MISSING_PARENT_RE, ('exec',))

    def test_invalid_literal(self):
        """ Test INVALID_LITERAL_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "invalid literal for int() with base 10: 'toto'"
        self.regex_matches(msg, INVALID_LITERAL_RE, ('int', 'toto'))

    def test_invalid_syntax(self):
        """ Test INVALID_SYNTAX_RE ."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy3
        msg = "invalid syntax"
        self.regex_matches(msg, INVALID_SYNTAX_RE, ())

    def test_invalid_comp(self):
        """ Test INVALID_COMP_RE ."""
        # PyPy3
        msg = "invalid comparison"
        self.regex_matches(msg, INVALID_COMP_RE, ())

    def test_expected_length(self):
        """ Test EXPECTED_LENGTH_RE ."""
        # PyPy
        msg = "expected length 3, got 2"
        self.regex_matches(msg, EXPECTED_LENGTH_RE, ('3', '2'))

    def test_future_first(self):
        """ Test FUTURE_FIRST_RE. """
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5
            "from __future__ imports must occur at the beginning of the file",
            # PyPy/PyPy3
            "__future__ statements must appear at beginning of file",
        ]
        for msg in msgs:
            self.regex_matches(msg, FUTURE_FIRST_RE, ())

    def test_future_feature_not_def(self):
        """ Test FUTURE_FEATURE_NOT_DEF_RE. """
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "future feature divisio is not defined"
        self.regex_matches(msg, FUTURE_FEATURE_NOT_DEF_RE, ('divisio',))


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


class AddStringToExcTest(unittest2.TestCase):
    """ Tests about add_string_to_exception. """

    def test_add_empty_string(self):
        """ Empty string added to NameError. """
        code = func_gen(param='babar', body='baba', args='0')
        type_, value, _ = get_exception(code)
        self.assertEqual(NameError, type_)
        str1, repres = str(value), repr(value)
        add_string_to_exception(value, "")
        str2, repres2 = str(value), repr(value)
        self.assertEqual(str1, str2)
        self.assertEqual(repres, repres2)

    def test_add_string(self):
        """ Non-empty string added to NameError. """
        string = "ABCDEF"
        code = func_gen(param='babar', body='baba', args='0')
        type_, value, _ = get_exception(code)
        self.assertEqual(NameError, type_)
        str1, repres = str(value), repr(value)
        add_string_to_exception(value, string)
        str2, repres2 = str(value), repr(value)
        self.assertEqual(str1 + string, str2)
        self.assertTrue(string not in repres, repres)
        self.assertTrue(string in repres2, repres2)

    def test_add_empty_string_to_syntaxerr(self):
        """ Empty string added to SyntaxError. """
        code = 'return'
        type_, value, _ = get_exception(code)
        self.assertEqual(SyntaxError, type_)
        str1, repres = str(value), repr(value)
        add_string_to_exception(value, "")
        str2, repres2 = str(value), repr(value)
        self.assertEqual(str1, str2)
        self.assertEqual(repres, repres2)

    def test_add_string_to_syntaxerr(self):
        """ Non-empty string added to SyntaxError. """
        string = "ABCDEF"
        code = 'return'
        type_, value, _ = get_exception(code)
        self.assertEqual(SyntaxError, type_)
        str1, repres = str(value), repr(value)
        add_string_to_exception(value, string)
        str2, repres2 = str(value), repr(value)
        self.assertNotEqual(str1, str2)
        self.assertTrue(string not in str1, str1)
        self.assertTrue(string in str2, str2)
        self.assertNotEqual(repres, repres2)
        self.assertTrue(string not in repres, repres)
        self.assertTrue(string in repres2, repres2)


class DecoratorTest(unittest2.TestCase):
    """ Tests about the didyoumean decorator. """
    deco = "@" + didyoumean.__name__ + "\n"

    def test_decorator_no_exception(self):
        """Check the case with no exception."""
        code = func_gen(param='babar', body='babar', args='0')
        no_exception(code)
        no_exception(self.deco + code)

    def test_decorator_suggestion(self):
        """Check the case with a suggestion."""
        type_ = NameError
        sugg = ". Did you mean 'babar'?"
        code = func_gen(param='babar', body='baba', args='0')
        type1, value1, _ = get_exception(code)
        type2, value2, _ = get_exception(self.deco + code)
        self.assertEqual(type1, type_)
        self.assertEqual(type2, type_)
        str1, str2 = str(value1), str(value2)
        repr1, repr2 = repr(value1), repr(value2)
        self.assertEqual(str1 + sugg, str2)
        self.assertNotEqual(repr1, repr2)
        self.assertTrue(sugg not in repr1, repr1)
        self.assertTrue(sugg in repr2, repr2)

    def test_decorator_no_suggestion(self):
        """Check the case with no suggestion."""
        type_ = NameError
        code = func_gen(param='babar', body='fdjhflsdsqfjlkqs', args='0')
        type1, value1, _ = get_exception(code)
        type2, value2, _ = get_exception(self.deco + code)
        self.assertEqual(type1, type_)
        self.assertEqual(type2, type_)
        self.assertEqual(str(value1), str(value2))
        self.assertEqual(repr(value1), repr(value2))

    def test_decorator_syntax(self):
        """Check the case with syntax error suggestion."""
        type_ = SyntaxError
        sugg = ". Did you mean to indent it, 'sys.exit([arg])'?"
        code = func_gen(body='exec("return")', args='')
        type1, value1, _ = get_exception(code)
        type2, value2, _ = get_exception(self.deco + code)
        self.assertEqual(type1, type_)
        self.assertEqual(type2, type_)
        str1, str2 = str(value1), str(value2)
        repr1, repr2 = repr(value1), repr(value2)
        self.assertNotEqual(str1, str2)
        self.assertTrue(sugg not in str1, str1)
        self.assertTrue(sugg in str2, str2)
        self.assertNotEqual(repr1, repr2)
        self.assertTrue(sugg not in repr1, repr1)
        self.assertTrue(sugg in repr2, repr2)


if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
