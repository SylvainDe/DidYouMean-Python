# -*- coding: utf-8
"""Unit tests for get_suggestions_for_exception."""
from didyoumean_internal import get_suggestions_for_exception, quote, \
    STAND_MODULES, AVOID_REC_MSG, \
    APPLY_REMOVED_MSG, BUFFER_REMOVED_MSG, CMP_REMOVED_MSG, \
    CMP_ARG_REMOVED_MSG, EXC_ATTR_REMOVED_MSG, LONG_REMOVED_MSG, \
    MEMVIEW_ADDED_MSG, RELOAD_REMOVED_MSG, STDERR_REMOVED_MSG, \
    NO_KEYWORD_ARG_MSG
import didyoumean_common_tests as common
import unittest2
import didyoumean_re as re
import warnings
import sys
import math
import os
import tempfile
from shutil import rmtree


this_is_a_global_list = []  # Value does not really matter but the type does


def func_gen(name='some_func', param='', body='pass', args=None):
    """Generate code corresponding to a function definition.

    Generate code for function definition (and eventually a call to it).
    Parameters are : name (with default), body (with default),
    parameters (with default) and arguments to call the functions with (if not
    provided or provided None, function call is not included in generated
    code).
    """
    func = "def {0}({1}):\n\t{2}\n".format(name, param, body)
    call = "" if args is None else "{0}({1})\n".format(name, args)
    return func + call


def my_generator():
    """Generate values for testing purposes.

    my_generator
    This is my generator, baby.
    """
    for i in range(5):
        yield i


def endlessly_recursive_func(n):
    """Call itself recursively with no end."""
    # http://stackoverflow.com/questions/871887/using-exec-with-recursive-functions
    return endlessly_recursive_func(n-1)


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

    def some_method2(self, x):
        """Method for testing purposes."""
        pass

    def _some_semi_private_method(self):
        """Method for testing purposes."""
        pass

    def __some_private_method(self):
        """Method for testing purposes."""
        pass

    def some_method_missing_self_arg():
        """Method for testing purposes."""
        pass

    def some_method_missing_self_arg2(x):
        """Method for testing purposes."""
        pass

    @classmethod
    def some_cls_method_missing_cls():
        """Class method for testing purposes."""
        pass

    @classmethod
    def some_cls_method_missing_cls2(x):
        """Class method for testing purposes."""
        pass


# More dummy classes
class CustomClass():
    """Custom class with nothing special."""

    pass


class IndexClass():
    """Custom class with __index__."""

    def __index__(self):
        """Dummy implementation of __index__."""
        return 2


class CallClass():
    """Custom class with __call__."""

    def __call__(self):  # arg list may differ
        """Dummy implementation of __call__."""
        return 0


class GetItemClass():
    """Custom class with __getitem__."""

    def __getitem__(self, key):
        """Dummy implementation of __getitem__."""
        return 0


class DelItemClass():
    """Custom class with __delitem__."""

    def __delitem__(self, key):
        """Dummy implementation of __delitem__."""
        pass


class SetItemClass():
    """Custom class with __setitem__."""

    def __setitem__(self, key, val):
        """Dummy implementation of __setitem__."""
        pass


class LenClass():
    """Custom class with __len__."""

    def __len__(self):
        """Dummy implementation of __len__."""
        return 0

# Logic to be able to have different tests on various version of Python
FIRST_VERSION = (0, 0)
LAST_VERSION = (10, 0)
ALL_VERSIONS = (FIRST_VERSION, LAST_VERSION)
INTERPRETERS = ['cython', 'pypy']


def from_version(version):
    """Create tuple describing a range of versions from a given version."""
    return (version, LAST_VERSION)


def up_to_version(version):
    """Create tuple describing a range of versions up to a given version."""
    return (FIRST_VERSION, version)


def before_and_after(version):
    """Return a tuple with the version ranges before/after a given version."""
    return up_to_version(version), from_version(version)


def before_mid_and_after(vers1, vers2):
    """Return a tuple with the versions before/in/after given versions."""
    assert vers1 < vers2
    return up_to_version(vers1), (vers1, vers2), from_version(vers2)


def version_in_range(version_range):
    """Test if current version is in a range version."""
    beg, end = version_range
    return beg <= sys.version_info < end


def interpreter_in(interpreters):
    """Test if current interpreter is in a list of interpreters."""
    is_pypy = hasattr(sys, "pypy_translation_info")
    interpreter = 'pypy' if is_pypy else 'cython'
    return interpreter in interpreters


def format_str(template, *args):
    """Format multiple string by using first arg as a template."""
    return [template.format(arg) for arg in args]


class PythonEnvRange(object):
    """Class to describe a (range of) Python environment.

    A range of Python environments consist of:
     - a range of Python version (tuple)
     - a list of interpreters (strings).
    """

    def __init__(self, version_range=None, interpreters=None):
        """Init a PythonEnvRange.

        The parameters are:
         - a range of version (optional - ALL if not provided)
         - a list of interpreters (optional - ALL if not provided).
            Also, a single interpreter can be provided.
        """
        self.interpreters = listify(interpreters, INTERPRETERS, str)
        self.version_range = \
            ALL_VERSIONS if version_range is None else version_range

    def contains_current_env(self):
        """Check if current environment is in PythonEnvRange object."""
        return version_in_range(self.version_range) and \
            interpreter_in(self.interpreters)


def listify(value, default, expected_types):
    """Return list from value, using default value if value is None."""
    if value is None:
        value = list(default)
    if not isinstance(value, list):
        value = [value]
    if default:
        assert all(v in default for v in value)
    if expected_types is not None:
        assert all(isinstance(v, expected_types) for v in value)
    return value


def get_exception(code):
    """Helper function to run code and get what it throws (or None)."""
    try:
        exec(code)
    except:
        return sys.exc_info()
    return None


# NameError for NameErrorTests
NAMEERROR = (NameError, re.NAMENOTDEFINED_RE)
NAMEERRORBEFOREREF = (NameError, re.VARREFBEFOREASSIGN_RE)
UNKNOWN_NAMEERROR = (NameError, None)
# UnboundLocalError for UnboundLocalErrorTests
UNBOUNDLOCAL = (UnboundLocalError, re.VARREFBEFOREASSIGN_RE)
UNKNOWN_UNBOUNDLOCAL = (UnboundLocalError, None)
# TypeError for TypeErrorTests
NBARGERROR = (TypeError, re.NB_ARG_RE)
MISSINGPOSERROR = (TypeError, re.MISSING_POS_ARG_RE)
UNHASHABLE = (TypeError, re.UNHASHABLE_RE)
UNSUBSCRIPTABLE = (TypeError, re.UNSUBSCRIPTABLE_RE)
CANNOTBEINTERPRETED = (TypeError, re.CANNOT_BE_INTERPRETED_INT_RE)
INTEXPECTED = (TypeError, re.INTEGER_EXPECTED_GOT_RE)
INDICESMUSTBEINT = (TypeError, re.INDICES_MUST_BE_INT_RE)
CANNOTBEINTERPRETEDINDEX = (
    TypeError,
    r"^object cannot be interpreted as an index$")
NOATTRIBUTE_TYPEERROR = (TypeError, re.ATTRIBUTEERROR_RE)
UNEXPECTEDKWARG = (TypeError, re.UNEXPECTED_KEYWORDARG_RE)
UNEXPECTEDKWARG2 = (TypeError, re.UNEXPECTED_KEYWORDARG2_RE)
UNEXPECTEDKWARG3 = (TypeError, re.UNEXPECTED_KEYWORDARG3_RE)
NOKWARGS = (TypeError, re.FUNC_TAKES_NO_KEYWORDARG_RE)
UNSUPPORTEDOPERAND = (TypeError, re.UNSUPPORTED_OP_RE)
BADOPERANDUNARY = (TypeError, re.BAD_OPERAND_UNARY_RE)
OBJECTDOESNOTSUPPORT = (TypeError, re.OBJ_DOES_NOT_SUPPORT_RE)
CANNOTCONCAT = (TypeError, re.CANNOT_CONCAT_RE)
ONLYCONCAT = (TypeError, re.ONLY_CONCAT_RE)
CANTCONVERT = (TypeError, re.CANT_CONVERT_RE)
MUSTBETYPENOTTYPE = (TypeError, re.MUST_BE_TYPE1_NOT_TYPE2_RE)
NOTCALLABLE = (TypeError, re.NOT_CALLABLE_RE)
DESCREXPECT = (TypeError, re.DESCRIPT_REQUIRES_TYPE_RE)
ARGNOTITERABLE = (TypeError, re.ARG_NOT_ITERABLE_RE)
MUSTCALLWITHINST = (TypeError, re.MUST_BE_CALLED_WITH_INST_RE)
OBJECTHASNOFUNC = (TypeError, re.OBJECT_HAS_NO_FUNC_RE)
EXCMUSTDERIVE = (TypeError, re.EXC_MUST_DERIVE_FROM_RE)
UNORDERABLE = (TypeError, re.UNORDERABLE_TYPES_RE)
OPNOTSUPPBETWEENINST = (TypeError, re.OP_NOT_SUPP_BETWEEN_INSTANCES_RE)
UNKNOWN_TYPEERROR = (TypeError, None)
# ImportError for ImportErrorTests
NOMODULE = (ImportError, re.NOMODULE_RE)
CANNOTIMPORT = (ImportError, re.CANNOTIMPORT_RE)
UNKNOWN_IMPORTERROR = (ImportError, None)
# KeyError for KeyErrorTests
KEYERROR = (KeyError, None)
# IndexError for IndexErrorTests
OUTOFRANGE = (IndexError, re.INDEXOUTOFRANGE_RE)
# ValueError for ValueErrorTests
TOOMANYVALUES = (ValueError, re.TOO_MANY_VALUES_UNPACK_RE)
NEEDMOREVALUES = (ValueError, re.NEED_MORE_VALUES_RE)
EXPECTEDLENGTH = (ValueError, re.EXPECTED_LENGTH_RE)
MATHDOMAIN = (ValueError, re.MATH_DOMAIN_ERROR_RE)
ZEROLENERROR = (ValueError, re.ZERO_LEN_FIELD_RE)
INVALIDLITERAL = (ValueError, re.INVALID_LITERAL_RE)
TIMEDATAFORMAT = (ValueError, re.TIME_DATA_DOES_NOT_MATCH_FORMAT_RE)
# AttributeError for AttributeErrorTests
ATTRIBUTEERROR = (AttributeError, re.ATTRIBUTEERROR_RE)
MODATTRIBUTEERROR = (AttributeError, re.MODULEHASNOATTRIBUTE_RE)
INSTHASNOMETH = (AttributeError, re.INSTANCE_HAS_NO_METH_RE)
UNKNOWN_ATTRIBUTEERROR = (AttributeError, None)
# SyntaxError for SyntaxErrorTests
INVALIDSYNTAX = (SyntaxError, re.INVALID_SYNTAX_RE)
INVALIDTOKEN = (SyntaxError, re.INVALID_TOKEN_RE)
NOBINDING = (SyntaxError, re.NO_BINDING_NONLOCAL_RE)
NONLOCALMODULE = (SyntaxError, re.NONLOCAL_AT_MODULE_RE)
UNEXPECTED_OEF = (SyntaxError, re.UNEXPECTED_EOF_RE)
OUTSIDEFUNC = (SyntaxError, re.OUTSIDE_FUNCTION_RE)
MISSINGPARENT = (SyntaxError, re.MISSING_PARENT_RE)
INVALIDCOMP = (SyntaxError, re.INVALID_COMP_RE)
FUTUREFIRST = (SyntaxError, re.FUTURE_FIRST_RE)
FUTFEATNOTDEF = (SyntaxError, re.FUTURE_FEATURE_NOT_DEF_RE)
UNQUALIFIED_EXEC = (SyntaxError, re.UNQUALIFIED_EXEC_RE)
IMPORTSTAR = (SyntaxError, re.IMPORTSTAR_RE)
# MemoryError and OverflowError for MemoryErrorTests
MEMORYERROR = (MemoryError, '')
OVERFLOWERR = (OverflowError, re.RESULT_TOO_MANY_ITEMS_RE)
# IOError
NOFILE_IO = (common.NoFileIoError, re.NO_SUCH_FILE_RE)
NOFILE_OS = (common.NoFileOsError, re.NO_SUCH_FILE_RE)
NOTADIR_IO = (common.NotDirIoError, "^Not a directory$")
NOTADIR_OS = (common.NotDirOsError, "^Not a directory$")
ISADIR_IO = (common.IsDirIoError, "^Is a directory$")
ISADIR_OS = (common.IsDirOsError, "^Is a directory$")
DIRNOTEMPTY_OS = (OSError, "^Directory not empty$")
# RuntimeError
MAXRECURDEPTH = (RuntimeError, re.MAX_RECURSION_DEPTH_RE)
SIZECHANGEDDURINGITER = (RuntimeError, re.SIZE_CHANGED_DURING_ITER_RE)


class GetSuggestionsTests(unittest2.TestCase):
    """Generic class to test get_suggestions_for_exception.

    Many tests do not correspond to any handled exceptions but are
    kept because it is quite convenient to have a large panel of examples.
    Also, some correspond to example where suggestions could be added, those
    are flagged with a NICE_TO_HAVE comment.
    Finally, whenever it is easily possible, the code with the suggestions
    taken into account is usually tested too to ensure that the suggestion does
    work.
    """

    def runs(self, code, version_range=None, interpreters=None):
        """Helper function to run code.

        version_range and interpreters can be provided if the test depends on
        the used environment.
        """
        details = "Running following code :\n---\n{0}\n---".format(code)
        if PythonEnvRange(version_range, interpreters).contains_current_env():
            exc = get_exception(code)
            self.assertTrue(exc is None, "Exc thrown : " + str(exc) + details)

    def throws(self, code, error_info,
               sugg=None, version_range=None, interpreters=None):
        """Run code and check it throws and relevant suggestions are provided.

        Helper function to run code, check that it throws, what it throws and
        that the exception leads to the expected suggestions.
        version_range and interpreters can be provided if the test depends on
        the used environment.
        """
        sugg = sorted(listify(sugg, [], str))
        error_type, error_msg = error_info
        details = "Running following code :\n---\n{0}\n---".format(code)
        if PythonEnvRange(version_range, interpreters).contains_current_env():
            exc = get_exception(code)
            self.assertFalse(exc is None, "No exc thrown." + details)
            type_caught, value, traceback = exc
            self.assertTrue(isinstance(value, type_caught))
            self.assertTrue(
                issubclass(type_caught, error_type),
                "{0} ({1}) not a subclass of {2}"
                .format(type_caught, value, error_type) + details)
            msg = next((a for a in value.args if isinstance(a, str)), '')
            if error_msg is not None:
                self.assertRegexpMatches(msg, error_msg, details)
            suggestions = sorted(
                get_suggestions_for_exception(value, traceback))
            self.assertEqual(suggestions, sugg, details)


class NameErrorTests(GetSuggestionsTests):
    """Class for tests related to NameError."""

    def test_local(self):
        """Should be 'foo'."""
        code = "foo = 0\n{0}"
        typo, good = "foob", "foo"
        sugg = "'{0}' (local)".format(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NAMEERROR, sugg)
        self.runs(good_code)

    def test_1_arg(self):
        """Should be 'foo'."""
        typo, good = "foob", "foo"
        sugg = "'{0}' (local)".format(good)
        code = func_gen(param=good, body='{0}', args='1')
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NAMEERROR, sugg)
        self.runs(good_code)

    def test_n_args(self):
        """Should be 'fool' or 'foot'."""
        typo, sugg1, sugg2 = "foob", "foot", "fool"
        code = func_gen(param='fool, foot', body='{0}', args='1, 2')
        suggs = ["'fool' (local)", "'foot' (local)"]
        bad, good1, good2 = format_str(code, typo, sugg1, sugg2)
        self.throws(bad, NAMEERROR, suggs)
        self.runs(good1)
        self.runs(good2)

    def test_builtin(self):
        """Should be 'max'."""
        typo, good = 'maxi', 'max'
        sugg = "'{0}' (builtin)".format(good)
        self.throws(typo, NAMEERROR, sugg)
        self.runs(good)

    def test_keyword(self):
        """Should be 'pass'."""
        typo, good = 'passs', 'pass'
        sugg = "'{0}' (keyword)".format(good)
        self.throws(typo, NAMEERROR, sugg)
        self.runs(good)

    def test_global(self):
        """Should be this_is_a_global_list."""
        typo, good = 'this_is_a_global_lis', 'this_is_a_global_list'
        # just a way to say that this_is_a_global_list is needed in globals
        this_is_a_global_list
        self.assertFalse(good in locals())
        self.assertTrue(good in globals())
        sugg = "'{0}' (global)".format(good)
        self.throws(typo, NAMEERROR, sugg)
        self.runs(good)

    def test_name(self):
        """Should be '__name__'."""
        typo, good = '__name_', '__name__'
        sugg = "'{0}' (global)".format(good)
        self.throws(typo, NAMEERROR, sugg)
        self.runs(good)

    def test_decorator(self):
        """Should be classmethod."""
        typo, good = "class_method", "classmethod"
        sugg = "'{0}' (builtin)".format(good)
        code = "@{0}\n" + func_gen()
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NAMEERROR, sugg)
        self.runs(good_code)

    def test_import(self):
        """Should be math."""
        code = 'import math\n{0}'
        typo, good = 'maths', 'math'
        sugg = "'{0}' (local)".format(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NAMEERROR, sugg)
        self.runs(good_code)

    def test_import2(self):
        """Should be my_imported_math."""
        code = 'import math as my_imported_math\n{0}'
        typo, good = 'my_imported_maths', 'my_imported_math'
        sugg = "'{0}' (local)".format(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NAMEERROR, sugg)
        self.runs(good_code)

    def test_imported(self):
        """Should be math.pi."""
        code = 'import math\n{0}'
        typo, good = 'pi', 'math.pi'
        sugg = quote(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NAMEERROR, sugg)
        self.runs(good_code)

    def test_imported_twice(self):
        """Should be math.pi."""
        code = 'import math\nimport math\n{0}'
        typo, good = 'pi', 'math.pi'
        sugg = quote(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NAMEERROR, sugg)
        self.runs(good_code)

    def test_not_imported(self):
        """Should be random.choice after importing random."""
        # This test assumes that `module` is not imported
        module, attr = 'random', 'choice'
        self.assertFalse(module in locals())
        self.assertFalse(module in globals())
        self.assertTrue(module in STAND_MODULES)
        bad_code = attr
        good_code = 'from {0} import {1}\n{2}'.format(module, attr, bad_code)
        sugg = "'{0}' from {1} (not imported)".format(attr, module)
        self.runs(good_code)
        self.throws(bad_code, NAMEERROR, sugg)

    def test_enclosing_scope(self):
        """Test that variables from enclosing scope are suggested."""
        # NICE_TO_HAVE
        typo, good = 'foob', 'foo'
        code = 'def f():\n\tfoo = 0\n\tdef g():\n\t\t{0}\n\tg()\nf()'
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NAMEERROR)
        self.runs(good_code)

    def test_no_sugg(self):
        """No suggestion."""
        self.throws('a = ldkjhfnvdlkjhvgfdhgf', NAMEERROR)

    def test_free_var_before_assignment(self):
        """No suggestion but different error message."""
        code = 'def f():\n\tdef g():\n\t\treturn free_var' \
               '\n\tg()\n\tfree_var = 0\nf()'
        self.throws(code, NAMEERRORBEFOREREF)

    # For added/removed names, following functions with one name
    # per functions were added in the early stages of the project.
    # In the future, I'd like to have them replaced by something
    # a bit more concise using relevant data structure. In the
    # meantime, I am keeping both versions because safer is better.
    def test_removed_cmp(self):
        """Builtin cmp is removed."""
        code = 'cmp(1, 2)'
        sugg1 = '1 < 2'
        sugg2 = 'def cmp(a, b):\n\treturn (a > b) - (a < b)\ncmp(1, 2)'
        before, after = before_and_after((3, 0, 1))
        self.runs(code, before)
        self.throws(code, NAMEERROR, CMP_REMOVED_MSG, after)
        self.runs(sugg1)
        self.runs(sugg2)

    def test_removed_reduce(self):
        """Builtin reduce is removed - moved to functools."""
        code = 'reduce(lambda x, y: x + y, [1, 2, 3, 4, 5])'
        new_code = 'from functools import reduce\n' + code
        sugg = "'reduce' from functools (not imported)"
        before, after = before_and_after((3, 0))
        self.runs(code, before)
        self.throws(code, NAMEERROR, sugg, after)
        self.runs(new_code, after)

    def test_removed_apply(self):
        """Builtin apply is removed."""
        code = 'apply(sum, [[1, 2, 3]])'
        good = 'sum([1, 2, 3])'
        before, after = before_and_after((3, 0))
        self.runs(code, before)
        self.throws(code, NAMEERROR, APPLY_REMOVED_MSG, after)
        self.runs(good)

    def test_removed_reload(self):
        """Builtin reload is removed.

        Moved to importlib.reload or imp.reload depending on version.
        """
        code = 'reload(math)'
        sugg_template = 'import {0}\n{0}.reload(math)'
        sugg1, sugg2 = format_str(sugg_template, 'importlib', 'imp')
        before, after = before_and_after((3, 0))
        self.runs(code, before)
        self.throws(code, NAMEERROR, RELOAD_REMOVED_MSG, after)
        self.runs(sugg1, from_version((3, 4)))
        self.runs(sugg2)

    def test_removed_intern(self):
        """Builtin intern is removed - moved to sys."""
        code = 'intern("toto")'
        new_code = 'sys.intern("toto")'
        suggs = ["'iter' (builtin)", "'sys.intern'"]
        before, after = before_and_after((3, 0))
        self.runs(code, before)
        self.throws(code, NAMEERROR, suggs, after)
        self.runs(new_code, after)

    def test_removed_execfile(self):
        """Builtin execfile is removed - use exec() and compile()."""
        # NICE_TO_HAVE
        code = 'execfile("some_filename")'
        _, after = before_and_after((3, 0))
        # self.runs(code, before)
        self.throws(code, NAMEERROR, [], after)

    def test_removed_raw_input(self):
        """Builtin raw_input is removed - use input() instead."""
        code = 'i = raw_input("Prompt:")'
        _, after = before_and_after((3, 0))
        # self.runs(code, before)
        self.throws(code, NAMEERROR, "'input' (builtin)", after)

    def test_removed_buffer(self):
        """Builtin buffer is removed - use memoryview instead."""
        code = 'buffer(b"abc")'
        new_code = 'memoryview(b"abc")'
        before, after = before_and_after((3, 0))
        self.runs(code, before)
        self.throws(code, NAMEERROR, BUFFER_REMOVED_MSG, after)
        self.runs(new_code, from_version((2, 7)))

    def test_added_2_7(self):
        """Test for names added in 2.7."""
        before, after = before_and_after((2, 7))
        for name, suggs in {
                'memoryview': [MEMVIEW_ADDED_MSG],
                }.items():
            self.throws(name, NAMEERROR, suggs, before)
            self.runs(name, after)

    def test_removed_3_0(self):
        """Test for names removed in 3.0."""
        before, after = before_and_after((3, 0))
        for name, suggs in {
                'StandardError': [STDERR_REMOVED_MSG],
                'apply': [APPLY_REMOVED_MSG],
                'basestring': [],
                'buffer': [BUFFER_REMOVED_MSG],
                'cmp': [CMP_REMOVED_MSG],
                'coerce': [],
                'execfile': [],
                'file': ["'filter' (builtin)"],
                'intern': ["'iter' (builtin)", "'sys.intern'"],
                'long': [LONG_REMOVED_MSG],
                'raw_input': ["'input' (builtin)"],
                'reduce': ["'reduce' from functools (not imported)"],
                'reload': [RELOAD_REMOVED_MSG],
                'unichr': [],
                'unicode': ["'code' (local)"],
                'xrange': ["'range' (builtin)"],
                }.items():
            self.runs(name, before)
            self.throws(name, NAMEERROR, suggs, after)

    def test_added_3_0(self):
        """Test for names added in 3.0."""
        before, after = before_and_after((3, 0))
        for name, suggs in {
                'ascii': [],
                'ResourceWarning': ["'FutureWarning' (builtin)"],
                '__build_class__': [],
                }.items():
            self.throws(name, NAMEERROR, suggs, before)
            self.runs(name, after)

    def test_added_3_3(self):
        """Test for names added in 3.3."""
        before, after = before_and_after((3, 3))
        for name, suggs in {
                'BrokenPipeError': [],
                'ChildProcessError': [],
                'ConnectionAbortedError': [],
                'ConnectionError': ["'IndentationError' (builtin)"],
                'ConnectionRefusedError': [],
                'ConnectionResetError': [],
                'FileExistsError': [],
                'FileNotFoundError': [],
                'InterruptedError': [],
                'IsADirectoryError': [],
                'NotADirectoryError': [],
                'PermissionError': ["'ZeroDivisionError' (builtin)"],
                'ProcessLookupError': ["'LookupError' (builtin)"],
                'TimeoutError': [],
                '__loader__': [],
                }.items():
            self.throws(name, NAMEERROR, suggs, before)
            self.runs(name, after)

    def test_added_3_4(self):
        """Test for names added in 3.4."""
        before, after = before_and_after((3, 4))
        for name, suggs in {
                '__spec__': [],
                }.items():
            self.throws(name, NAMEERROR, suggs, before)
            self.runs(name, after)

    def test_added_3_5(self):
        """Test for names added in 3.5."""
        before, after = before_and_after((3, 5))
        for name, suggs in {
                'StopAsyncIteration': ["'StopIteration' (builtin)"],
                }.items():
            self.throws(name, NAMEERROR, suggs, before)
            self.runs(name, after)

    def test_import_sugg(self):
        """Should import module first."""
        module = 'collections'
        sugg = 'import {0}'.format(module)
        typo, good_code = module, sugg + '\n' + module
        self.assertFalse(module in locals())
        self.assertFalse(module in globals())
        self.assertTrue(module in STAND_MODULES)
        suggestions = (
            # module.module is suggested on Python 3.3 :-/
            ["'{0}' from {1} (not imported)".format(module, module)]
            if version_in_range(((3, 3), (3, 4))) else []) + \
            ['to {0} first'.format(sugg)]
        self.throws(typo, NAMEERROR, suggestions)
        self.runs(good_code)

    def test_attribute_hidden(self):
        """Should be math.pi but module math is hidden."""
        math  # just a way to say that math module is needed in globals
        self.assertFalse('math' in locals())
        self.assertTrue('math' in globals())
        code = 'math = ""\npi'
        sugg = "'math.pi' (global hidden by local)"
        self.throws(code, NAMEERROR, sugg)

    def test_self(self):
        """"Should be self.babar."""
        code = 'FoobarClass().nameerror_self()'
        sugg = "'self.babar'"
        self.throws(code, NAMEERROR, sugg)

    def test_self2(self):
        """Should be self.this_is_cls_mthd."""
        code = 'FoobarClass().nameerror_self2()'
        suggs = ["'FoobarClass.this_is_cls_mthd'", "'self.this_is_cls_mthd'"]
        self.throws(code, NAMEERROR, suggs)

    def test_cls(self):
        """Should be cls.this_is_cls_mthd."""
        code = 'FoobarClass().nameerror_cls()'
        suggs = ["'FoobarClass.this_is_cls_mthd'", "'cls.this_is_cls_mthd'"]
        self.throws(code, NAMEERROR, suggs)

    def test_complex_numbers(self):
        """Should be 1j."""
        code = 'assert {0} ** 2 == -1'
        good = '1j'
        good_code, bad_code_i, bad_code_j = format_str(code, good, 'i', 'j')
        sugg = "'{0}' (imaginary unit)".format(good)
        self.throws(bad_code_i, NAMEERROR, sugg)
        self.throws(bad_code_j, NAMEERROR, sugg)
        self.runs(good_code)

    def test_shell_commands(self):
        """Trying shell commands."""
        cmd, good = 'ls', 'os.listdir(os.getcwd())'
        self.throws(cmd, NAMEERROR, quote(good))
        self.runs(good)
        cmd, good = 'pwd', 'os.getcwd()'
        self.throws(cmd, NAMEERROR, quote(good))
        self.runs(good)
        cmd, good = 'cd', 'os.chdir(path)'
        self.throws(cmd, NAMEERROR, quote(good))
        self.runs(good.replace('path', 'os.getcwd()'))
        cmd = 'rm'
        sugg = "'os.remove(filename)', 'shutil.rmtree(dir)' for recursive"
        self.throws(cmd, NAMEERROR, sugg)

    def test_unmatched_msg(self):
        """Test that arbitrary strings are supported."""
        code = 'raise NameError("unmatched NAMEERROR")'
        self.throws(code, UNKNOWN_NAMEERROR)


class UnboundLocalErrorTests(GetSuggestionsTests):
    """Class for tests related to UnboundLocalError."""

    def test_unbound_typo(self):
        """Should be foo."""
        code = 'def func():\n\tfoo = 1\n\t{0} +=1\nfunc()'
        typo, good = "foob", "foo"
        sugg = "'{0}' (local)".format(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, UNBOUNDLOCAL, sugg)
        self.runs(good_code)

    def test_unbound_global(self):
        """Should be global nb."""
        # NICE_TO_HAVE
        code = 'nb = 0\ndef func():\n\t{0}\n\tnb +=1\nfunc()'
        sugg = 'global nb'
        bad_code, good_code = format_str(code, "", sugg)
        original_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(1000)  # needed for weird PyPy versions
        self.throws(bad_code, UNBOUNDLOCAL)
        self.runs(good_code)  # this is to be run afterward :-/
        sys.setrecursionlimit(original_limit)

    def test_unbound_nonlocal(self):
        """Shoud be nonlocal nb."""
        # NICE_TO_HAVE
        code = 'def foo():\n\tnb = 0\n\tdef bar():' \
               '\n\t\t{0}\n\t\tnb +=1\n\tbar()\nfoo()'
        sugg = 'nonlocal nb'
        bad_code, good_code = format_str(code, "", sugg)
        self.throws(bad_code, UNBOUNDLOCAL)
        before, after = before_and_after((3, 0))
        self.throws(good_code, INVALIDSYNTAX, [], before)
        self.runs(good_code, after)

    def test_unbound_nonlocal_and_global(self):
        """Shoud be nonlocal nb or global."""
        # NICE_TO_HAVE
        code = 'nb = 1\ndef foo():\n\tnb = 0\n\tdef bar():' \
               '\n\t\t{0}\n\t\tnb +=1\n\tbar()\nfoo()'
        sugg1, sugg2 = 'nonlocal nb', 'global nb'
        bad_code, good_code1, good_code2 = format_str(code, "", sugg1, sugg2)
        self.throws(bad_code, UNBOUNDLOCAL)
        self.runs(good_code2)
        before, after = before_and_after((3, 0))
        self.throws(good_code1, INVALIDSYNTAX, [], before)
        self.runs(good_code1, after)

    def test_unmatched_msg(self):
        """Test that arbitrary strings are supported."""
        code = 'raise UnboundLocalError("unmatched UNBOUNDLOCAL")'
        self.throws(code, UNKNOWN_UNBOUNDLOCAL)


class AttributeErrorTests(GetSuggestionsTests):
    """Class for tests related to AttributeError."""

    def test_nonetype(self):
        """In-place methods like sort returns None.

        Might also happen if the functions misses a return.
        """
        # NICE_TO_HAVE
        code = '[].sort().append(4)'
        self.throws(code, ATTRIBUTEERROR)

    def test_method(self):
        """Should be 'append'."""
        code = '[0].{0}(1)'
        typo, good = 'appendh', 'append'
        sugg = quote(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, ATTRIBUTEERROR, sugg)
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
        sugg = "'next(generator)'"
        before, after = before_and_after((3, 0))
        self.runs(code, before)
        self.throws(code, ATTRIBUTEERROR, sugg, after)
        self.runs(new_code)

    def test_wrongmethod(self):
        """Should be 'lst.append(1)'."""
        code = '[0].{0}(1)'
        typo, good = 'add', 'append'
        sugg = quote(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, ATTRIBUTEERROR, sugg)
        self.runs(good_code)

    def test_wrongmethod2(self):
        """Should be 'lst.extend([4, 5, 6])'."""
        code = '[0].{0}([4, 5, 6])'
        typo, good = 'update', 'extend'
        sugg = quote(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, ATTRIBUTEERROR, sugg)
        self.runs(good_code)

    def test_hidden(self):
        """Accessing wrong string object."""
        # NICE_TO_HAVE
        code = 'import string\nstring = "a"\nascii = string.ascii_letters'
        self.throws(code, ATTRIBUTEERROR)

    def test_no_sugg(self):
        """No suggestion."""
        self.throws('[1, 2, 3].ldkjhfnvdlkjhvgfdhgf', ATTRIBUTEERROR)

    def test_from_module(self):
        """Should be math.pi."""
        code = 'import math\nmath.{0}'
        typo, good = 'pie', 'pi'
        sugg = quote(good)
        before, after = before_and_after((3, 5))
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, ATTRIBUTEERROR, sugg, before)
        self.throws(bad_code, MODATTRIBUTEERROR, sugg, after)
        self.runs(good_code)

    def test_from_module2(self):
        """Should be math.pi."""
        code = 'import math\nm = math\nm.{0}'
        typo, good = 'pie', 'pi'
        sugg = quote(good)
        before, after = before_and_after((3, 5))
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, ATTRIBUTEERROR, sugg, before)
        self.throws(bad_code, MODATTRIBUTEERROR, sugg, after)
        self.runs(good_code)

    def test_from_class(self):
        """Should be 'this_is_cls_mthd'."""
        code = 'FoobarClass().{0}()'
        typo, good = 'this_is_cls_mth', 'this_is_cls_mthd'
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, ATTRIBUTEERROR, sugg)
        self.runs(good_code)

    def test_from_class2(self):
        """Should be 'this_is_cls_mthd'."""
        code = 'FoobarClass.{0}()'
        typo, good = 'this_is_cls_mth', 'this_is_cls_mthd'
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, ATTRIBUTEERROR, sugg)
        self.runs(good_code)

    def test_private_attr(self):
        """Test that 'private' members are suggested with a warning message.

        Sometimes 'private' members are suggested but it's not ideal, a
        warning must be added to the suggestion.
        """
        code = 'FoobarClass().{0}'
        method = '__some_private_method'
        method2 = '_some_semi_private_method'
        typo, priv, good = method, '_FoobarClass' + method, method2
        suggs = ["'{0}' (but it is supposed to be private)".format(priv),
                 "'{0}'".format(good)]
        bad_code, priv_code, good_code = format_str(code, typo, priv, good)
        self.throws(bad_code, ATTRIBUTEERROR, suggs)
        self.runs(priv_code)
        self.runs(good_code)

    def test_get_on_nondict_cont(self):
        """Method get does not exist on all containers."""
        code = '{0}().get(0, None)'
        dictcode, tuplecode, listcode, setcode = \
            format_str(code, 'dict', 'tuple', 'list', 'set')
        self.runs(dictcode)
        self.throws(setcode, ATTRIBUTEERROR)
        for bad_code in tuplecode, listcode:
            self.throws(bad_code, ATTRIBUTEERROR,
                        "'obj[key]' with a len() check or "
                        "try: except: KeyError or IndexError")

    def test_removed_has_key(self):
        """Method has_key is removed from dict."""
        code = 'dict().has_key(1)'
        new_code = '1 in dict()'
        sugg = "'key in dict' (has_key is removed)"
        before, after = before_and_after((3, 0))
        self.runs(code, before)
        self.throws(code, ATTRIBUTEERROR, sugg, after)
        self.runs(new_code)

    def test_removed_dict_methods(self):
        """Different methos (iterXXX) have been removed from dict."""
        before, after = before_and_after((3, 0))
        code = 'dict().{0}()'
        for method, sugg in {
            'iterkeys': [],
            'itervalues': ["'values'"],
            'iteritems': ["'items'"],
        }.items():
            meth_code, = format_str(code, method)
            self.runs(meth_code, before)
            self.throws(meth_code, ATTRIBUTEERROR, sugg, after)

    def test_remove_exc_attr(self):
        """Attribute sys.exc_xxx have been removed."""
        before, mid, after = before_mid_and_after((3, 0), (3, 5))
        for att_name, sugg in {
            'exc_type': [EXC_ATTR_REMOVED_MSG],
            'exc_value': [EXC_ATTR_REMOVED_MSG],
            'exc_traceback': ["'last_traceback'", EXC_ATTR_REMOVED_MSG],
        }.items():
            code = 'import sys\nsys.' + att_name
            if att_name == 'exc_type':
                self.runs(code, before)  # others may be undef
            self.runs(code, mid, 'pypy')
            self.throws(code, ATTRIBUTEERROR, sugg, mid, 'cython')
            self.throws(code, MODATTRIBUTEERROR, sugg, after)
        self.runs('import sys\nsys.exc_info()')

    def test_removed_xreadlines(self):
        """Method xreadlines is removed."""
        # NICE_TO_HAVE
        code = "import os\nwith open(os.path.realpath(__file__)) as f:" \
            "\n\tf.{0}"
        old, good1, good2 = 'xreadlines', 'readline', 'readlines'
        suggs = [quote(good1), quote(good2), "'writelines'"]
        old_code, new_code1, new_code2 = format_str(code, old, good1, good2)
        before, after = before_and_after((3, 0))
        self.runs(old_code, before)
        self.throws(old_code, ATTRIBUTEERROR, suggs, after)
        self.runs(new_code1)
        self.runs(new_code2)

    def test_removed_function_attributes(self):
        """Some functions attributes are removed."""
        # NICE_TO_HAVE
        before, after = before_and_after((3, 0))
        code = func_gen() + 'some_func.{0}'
        attributes = [('func_name', '__name__', []),
                      ('func_doc', '__doc__', []),
                      ('func_defaults', '__defaults__', ["'__defaults__'"]),
                      ('func_dict', '__dict__', []),
                      ('func_closure', '__closure__', []),
                      ('func_globals', '__globals__', []),
                      ('func_code', '__code__', [])]
        for (old_att, new_att, sugg) in attributes:
            old_code, new_code = format_str(code, old_att, new_att)
            self.runs(old_code, before)
            self.throws(old_code, ATTRIBUTEERROR, sugg, after)
            self.runs(new_code)

    def test_removed_method_attributes(self):
        """Some methods attributes are removed."""
        # NICE_TO_HAVE
        before, after = before_and_after((3, 0))
        code = 'FoobarClass().some_method.{0}'
        attributes = [('im_func', '__func__', []),
                      ('im_self', '__self__', []),
                      ('im_class', '__self__.__class__', ["'__class__'"])]
        for (old_att, new_att, sugg) in attributes:
            old_code, new_code = format_str(code, old_att, new_att)
            self.runs(old_code, before)
            self.throws(old_code, ATTRIBUTEERROR, sugg, after)
            self.runs(new_code)

    def test_moved_between_str_string(self):
        """Some methods have been moved from string to str."""
        # NICE_TO_HAVE
        version1 = (3, 0)
        version2 = (3, 5)
        code = 'import string\n{0}.maketrans'
        code_str, code_string = format_str(code, 'str', 'string')
        code_str2 = 'str.maketrans'  # No 'string' import
        code_str3 = 'import string as my_string\nstr.maketrans'  # Named import
        self.throws(code_str, ATTRIBUTEERROR, [], up_to_version(version1))
        self.throws(code_str2, ATTRIBUTEERROR, [], up_to_version(version1))
        self.throws(code_str3, ATTRIBUTEERROR, [], up_to_version(version1))
        self.runs(code_string, up_to_version(version1))
        self.throws(code_string, ATTRIBUTEERROR, [], (version1, version2))
        self.throws(code_string, MODATTRIBUTEERROR, [], from_version(version2))
        self.runs(code_str, from_version(version1))
        self.runs(code_str2, from_version(version1))
        self.runs(code_str3, from_version(version1))

    def test_moved_between_imp_importlib(self):
        """Some methods have been moved from imp to importlib."""
        # NICE_TO_HAVE
        # reload removed from Python 3
        # importlib module new in Python 2.7
        # importlib.reload new in Python 3.4
        # imp.reload new in Python 3.2
        version27 = (2, 7)
        version3 = (3, 0)
        version26 = up_to_version(version27)
        code = '{0}reload(math)'
        null, code_imp, code_importlib = format_str(
            code, '', 'import imp\nimp.', 'import importlib\nimportlib.')
        self.runs(null, up_to_version(version3))
        self.throws(null, NAMEERROR,
                    RELOAD_REMOVED_MSG, from_version(version3))
        self.runs(code_imp)
        self.throws(code_importlib, NOMODULE, [], version26)
        self.throws(code_importlib, ATTRIBUTEERROR,
                    "'reload(module)'", (version27, version3))
        self.throws(code_importlib, ATTRIBUTEERROR,
                    [], (version3, (3, 4)))
        self.runs(code_importlib, from_version((3, 4)))

    def test_join(self):
        """Test what happens when join is used incorrectly.

        This can be frustrating to call join on an iterable instead of a
        string.
        """
        code = "['a', 'b'].join('-')"
        self.throws(code, ATTRIBUTEERROR, "'my_string.join(list)'")

    def test_set_dict_comprehension(self):
        """{} creates a dict and not an empty set leading to errors."""
        # NICE_TO_HAVE
        before, after = before_and_after((2, 7))
        for method in set(dir(set)) - set(dir(dict)):
            if not method.startswith('__'):  # boring suggestions
                code = "a = {0}\na." + method
                typo, dict1, dict2, sugg, set1 = format_str(
                    code, "{}", "dict()", "{0: 0}", "set()", "{0}")
                self.throws(typo, ATTRIBUTEERROR)
                self.throws(dict1, ATTRIBUTEERROR)
                self.throws(dict2, ATTRIBUTEERROR)
                self.runs(sugg)
                self.throws(set1, INVALIDSYNTAX, [], before)
                self.runs(set1, after)

    def test_unmatched_msg(self):
        """Test that arbitrary strings are supported."""
        code = 'raise AttributeError("unmatched ATTRIBUTEERROR")'
        self.throws(code, UNKNOWN_ATTRIBUTEERROR)

    # TODO: Add sugg for situation where self/cls is the missing parameter


class TypeErrorTests(GetSuggestionsTests):
    """Class for tests related to TypeError."""

    def test_unhashable(self):
        """Test for UNHASHABLE exception."""
        # NICE_TO_HAVE : suggest hashable equivalent
        self.throws('s = set([list()])', UNHASHABLE)
        self.throws('s = set([dict()])', UNHASHABLE)
        self.throws('s = set([set()])', UNHASHABLE)
        self.runs('s = set([tuple()])')
        self.runs('s = set([frozenset()])')

    def test_not_sub(self):
        """Should be function call, not [] operator."""
        # https://twitter.com/raymondh/status/772957699478663169
        typo, good = '[2]', '(2)'
        code = func_gen(param='a') + 'some_func{0}'
        bad_code, good_code = format_str(code, typo, good)
        suggestion = "'function(value)'"
        suggs = ["'__get__'", "'__getattribute__'", suggestion]
        # Only Python 2.7 with cpython has a different error message
        # (leading to more suggestions based on fuzzy matches)
        before, mid, after = before_mid_and_after((2, 7), (3, 0))
        self.throws(bad_code, UNSUBSCRIPTABLE, suggestion, interpreters='pypy')
        self.throws(bad_code, UNSUBSCRIPTABLE, suggestion, before, 'cython')
        self.throws(bad_code, NOATTRIBUTE_TYPEERROR, suggs, mid, 'cython')
        self.throws(bad_code, UNSUBSCRIPTABLE, suggestion, after, 'cython')
        self.runs(good_code)

    def test_method_called_on_class(self):
        """Test where a method is called on a class and not an instance.

        Forgetting parenthesis makes the difference between using an
        instance and using a type.
        """
        # NICE_TO_HAVE
        wrong_type = (DESCREXPECT, MUSTCALLWITHINST, NBARGERROR)
        not_iterable = (ARGNOTITERABLE, ARGNOTITERABLE, ARGNOTITERABLE)
        before, after = before_and_after((3, 0))
        for code, (err_cy, err_pyp, err_pyp3) in [
                ('set{0}.add(0)', wrong_type),
                ('list{0}.append(0)', wrong_type),
                ('0 in list{0}', not_iterable)]:
            bad_code, good_code = format_str(code, '', '()')
            self.runs(good_code)
            self.throws(bad_code, err_cy, interpreters='cython')
            self.throws(bad_code, err_pyp, [], before, 'pypy')
            self.throws(bad_code, err_pyp3, [], after, 'pypy')

    def test_set_operations(self):
        """+, +=, etc doesn't work on sets. A suggestion would be nice."""
        # NICE_TO_HAVE
        typo1 = 'set() + set()'
        typo2 = 's = set()\ns += set()'
        code1 = 'set() | set()'
        code2 = 'set().union(set())'
        code3 = 'set().update(set())'
        self.throws(typo1, UNSUPPORTEDOPERAND)
        self.throws(typo2, UNSUPPORTEDOPERAND)
        self.runs(code1)
        self.runs(code2)
        self.runs(code3)

    def test_dict_operations(self):
        """+, +=, etc doesn't work on dicts. A suggestion would be nice."""
        # NICE_TO_HAVE
        typo1 = 'dict() + dict()'
        typo2 = 'd = dict()\nd += dict()'
        typo3 = 'dict() & dict()'
        self.throws(typo1, UNSUPPORTEDOPERAND)
        self.throws(typo2, UNSUPPORTEDOPERAND)
        self.throws(typo3, UNSUPPORTEDOPERAND)
        code1 = 'dict().update(dict())'
        self.runs(code1)

    def test_unsupported_operand_caret(self):
        """Use '**' for power, not '^'."""
        code = '3.5 {0} 2'
        bad_code, good_code = format_str(code, '^', '**')
        self.runs(good_code)
        self.throws(bad_code, UNSUPPORTEDOPERAND, "'val1 ** val2'")

    def test_unary_operand_custom(self):
        """Test unary operand errors on custom types."""
        before, after = before_and_after((3, 0))
        ops = {
            '+{0}': ('__pos__', "'__doc__'"),
            '-{0}': ('__neg__', None),
            '~{0}': ('__invert__', None),
            'abs({0})': ('__abs__', None),
        }
        obj = 'CustomClass()'
        sugg = 'implement "{0}" on CustomClass'
        for op, suggestions in ops.items():
            code = op.format(obj)
            magic, sugg_attr = suggestions
            sugg_unary = sugg.format(magic)
            self.throws(code, ATTRIBUTEERROR, sugg_attr, before)
            self.throws(code, BADOPERANDUNARY, sugg_unary, after)

    def test_unary_operand_builtin(self):
        """Test unary operand errors on builtin types."""
        ops = [
            '+{0}',
            '-{0}',
            '~{0}',
            'abs({0})',
        ]
        obj = 'set()'
        for op in ops:
            code = op.format(obj)
            self.throws(code, BADOPERANDUNARY)

    def test_len_on_iterable(self):
        """len() can't be called on iterable (weird but understandable)."""
        code = 'len(my_generator())'
        sugg = 'len(list(my_generator()))'
        self.throws(code, OBJECTHASNOFUNC, "'len(list(generator))'")
        self.runs(sugg)

    def test_len_on_custom(self):
        """len() can't be called on custom."""
        before, after = before_and_after((3, 0))
        code = 'o = {0}()\nlen(o)'
        bad, good = format_str(code, 'CustomClass', 'LenClass')
        sugg = 'implement "__len__" on CustomClass'
        self.throws(bad, ATTRIBUTEERROR, ["'__module__'"], before)
        self.throws(bad, OBJECTHASNOFUNC, sugg, after)
        self.runs(good)

    def test_nb_args(self):
        """Should have 1 arg."""
        typo, good = '1, 2', '1'
        code = func_gen(param='a', args='{0}')
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NBARGERROR)
        self.runs(good_code)

    def test_nb_args1(self):
        """Should have 0 args."""
        typo, good = '1', ''
        code = func_gen(param='', args='{0}')
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NBARGERROR)
        self.runs(good_code)

    def test_nb_args2(self):
        """Should have 1 arg."""
        typo, good = '', '1'
        before, after = before_and_after((3, 3))
        code = func_gen(param='a', args='{0}')
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NBARGERROR, [], before)
        self.throws(bad_code, MISSINGPOSERROR, [], after)
        self.runs(good_code)

    def test_nb_args3(self):
        """Should have 3 args."""
        typo, good = '1', '1, 2, 3'
        before, after = before_and_after((3, 3))
        code = func_gen(param='so, much, args', args='{0}')
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NBARGERROR, [], before)
        self.throws(bad_code, MISSINGPOSERROR, [], after)
        self.runs(good_code)

    def test_nb_args4(self):
        """Should have 3 args."""
        typo, good = '', '1, 2, 3'
        before, after = before_and_after((3, 3))
        code = func_gen(param='so, much, args', args='{0}')
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NBARGERROR, [], before)
        self.throws(bad_code, MISSINGPOSERROR, [], after)
        self.runs(good_code)

    def test_nb_args5(self):
        """Should have 3 args."""
        typo, good = '1, 2', '1, 2, 3'
        before, after = before_and_after((3, 3))
        code = func_gen(param='so, much, args', args='{0}')
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NBARGERROR, [], before)
        self.throws(bad_code, MISSINGPOSERROR, [], after)
        self.runs(good_code)

    def test_nb_args6(self):
        """Should provide more args."""
        # Amusing message: 'func() takes exactly 2 arguments (2 given)'
        before, after = before_and_after((3, 3))
        code = func_gen(param='a, b, c=3', args='{0}')
        bad_code, good_code1, good_code2 = format_str(
            code,
            'b=2, c=3',
            'a=1, b=2, c=3',
            '1, b=2, c=3')
        self.throws(bad_code, NBARGERROR, [], before)
        self.throws(bad_code, MISSINGPOSERROR, [], after)
        self.runs(good_code1)
        self.runs(good_code2)

    def test_nb_arg7(self):
        """More tests."""
        code = 'dict().get(1, 2, 3)'
        self.throws(code, NBARGERROR)

    def test_nb_arg8(self):
        """More tests."""
        code = 'dict().get()'
        self.throws(code, NBARGERROR)

    def test_nb_arg_missing_self(self):
        """Arg 'self' is missing."""
        # NICE_TO_HAVE
        obj = 'FoobarClass()'
        self.throws(obj + '.some_method_missing_self_arg()', NBARGERROR)
        self.throws(obj + '.some_method_missing_self_arg2(42)', NBARGERROR)
        self.runs(obj + '.some_method()')
        self.runs(obj + '.some_method2(42)')

    def test_nb_arg_missing_cls(self):
        """Arg 'cls' is missing."""
        # NICE_TO_HAVE
        for obj in ('FoobarClass()', 'FoobarClass'):
            self.throws(obj + '.some_cls_method_missing_cls()', NBARGERROR)
            self.throws(obj + '.some_cls_method_missing_cls2(42)', NBARGERROR)
            self.runs(obj + '.this_is_cls_mthd()')

    def test_keyword_args(self):
        """Should be param 'babar' not 'a' but it's hard to guess."""
        typo, good = 'a', 'babar'
        code = func_gen(param=good, args='{0}=1')
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, UNEXPECTEDKWARG)
        self.runs(good_code)

    def test_keyword_args2(self):
        """Should be param 'abcdef' not 'abcdf'."""
        typo, good = 'abcdf', 'abcdef'
        code = func_gen(param=good, args='{0}=1')
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, UNEXPECTEDKWARG, sugg)
        self.runs(good_code)

    def test_keyword_arg_method(self):
        """Should be the same as previous test but on a method."""
        code = 'class MyClass:\n\tdef func(self, a):' \
               '\n\t\tpass\nMyClass().func({0}=1)'
        bad_code, good_code = format_str(code, 'babar', 'a')
        self.throws(bad_code, UNEXPECTEDKWARG)
        self.runs(good_code)

    def test_keyword_arg_method2(self):
        """Should be the same as previous test but on a method."""
        typo, good = 'abcdf', 'abcdef'
        code = 'class MyClass:\n\tdef func(self, ' + good + '):' \
               '\n\t\tpass\nMyClass().func({0}=1)'
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, UNEXPECTEDKWARG, sugg)
        self.runs(good_code)

    def test_keyword_arg_class_method(self):
        """Should be the same as previous test but on a class method."""
        code = 'class MyClass:\n\t@classmethod\n\tdef func(cls, a):' \
               '\n\t\tpass\nMyClass.func({0}=1)'
        bad_code, good_code = format_str(code, 'babar', 'a')
        self.throws(bad_code, UNEXPECTEDKWARG)
        self.runs(good_code)

    def test_keyword_arg_class_method2(self):
        """Should be the same as previous test but on a class method."""
        typo, good = 'abcdf', 'abcdef'
        code = 'class MyClass:\n\t@classmethod ' \
               '\n\tdef func(cls, ' + good + '):\n ' \
               '\t\tpass\nMyClass.func({0}=1)'
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, UNEXPECTEDKWARG, sugg)
        self.runs(good_code)

    def test_keyword_arg_multiples_instances(self):
        """If multiple functions are found, suggestions should be unique."""
        typo, good = 'abcdf', 'abcdef'
        code = 'class MyClass:\n\tdef func(self, ' + good + '):' \
               '\n\t\tpass\na = MyClass()\nb = MyClass()\na.func({0}=1)'
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, UNEXPECTEDKWARG, sugg)
        self.runs(good_code)

    def test_keyword_arg_lambda(self):
        """Test with lambda functions instead of usual function."""
        typo, good = 'abcdf', 'abcdef'
        sugg = quote(good)
        code = 'f = lambda arg1, ' + good + ': None\nf(42, {0}=None)'
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, UNEXPECTEDKWARG, sugg)
        self.runs(good_code)

    def test_keyword_arg_lambda_method(self):
        """Test with lambda methods instead of usual methods."""
        typo, good = 'abcdf', 'abcdef'
        sugg = quote(good)
        code = 'class MyClass:\n\tfunc = lambda self, ' + good + ': None' \
               '\nMyClass().func({0}=1)'
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, UNEXPECTEDKWARG, sugg)
        self.runs(good_code)

    def test_keyword_arg_other_objects_with_name(self):
        """Mix of previous tests but with more objects defined.

        Non-function object with same same as the function tested are defined
        to ensure that things do work fine.
        """
        code = 'func = "not_a_func"\nclass MyClass:\n\tdef func(self, a):' \
               '\n\t\tpass\nMyClass().func({0}=1)'
        bad_code, good_code = format_str(code, 'babar', 'a')
        self.throws(bad_code, UNEXPECTEDKWARG)
        self.runs(good_code)

    def test_keyword_builtin(self):
        """A few builtins (like int()) have a different error message."""
        # NICE_TO_HAVE
        # 'max', 'input', 'len', 'abs', 'all', etc have a specific error
        # message and are not relevant here
        for builtin in ['int', 'float', 'bool', 'complex']:
            code = builtin + '(this_doesnt_exist=2)'
            self.throws(code, UNEXPECTEDKWARG2, interpreters='cython')
            self.throws(code, UNEXPECTEDKWARG, interpreters='pypy')

    def test_keyword_builtin_print(self):
        """Builtin "print" has a different error message."""
        # It would be NICE_TO_HAVE suggestions on keyword arguments
        before, after = before_and_after((3, 0))
        code = "c = 'string'\nb = print(c, end_='toto')"
        self.throws(code, INVALIDSYNTAX, [], before)
        self.throws(code, UNEXPECTEDKWARG2, [], after, 'cython')
        self.throws(code, UNEXPECTEDKWARG3, [], after, 'pypy')

    def test_keyword_sort_cmpkey(self):
        """Sort and sorted functions have a cmp/key param dep. on the vers."""
        before, after = before_and_after((3, 0))
        code = "import functools as f\nl = [1, 8, 3]\n" \
               "def comp(a, b): return (a > b) - (a < b)\nl.sort({0})"
        sugg = CMP_ARG_REMOVED_MSG
        cmp_arg, key_arg, cmp_to_key = format_str(
                code, 'cmp=comp', 'key=id', 'key=f.cmp_to_key(comp)')
        self.runs(cmp_arg, before)
        self.throws(cmp_arg, UNEXPECTEDKWARG2, sugg, after, 'cython')
        self.throws(cmp_arg, UNEXPECTEDKWARG, sugg, after, 'pypy')
        self.runs(key_arg)
        self.runs(cmp_to_key, from_version((2, 7)))

    def test_c_func_takes_no_keyword_arguments(self):
        """TODO."""
        # http://stackoverflow.com/questions/24463202/typeerror-get-takes-no-keyword-arguments
        # https://www.python.org/dev/peps/pep-0457/
        # https://www.python.org/dev/peps/pep-0436/#functions-with-positional-only-parameters
        sugg = NO_KEYWORD_ARG_MSG
        code = 'dict().get(0, {0}None)'
        good_code, bad_code = format_str(code, '', 'default=')
        self.runs(good_code)
        self.throws(bad_code, NOKWARGS, sugg, interpreters='cython')
        self.runs(bad_code, interpreters='pypy')
        # It would be better to have the suggestion only when the function
        # doesn't accept keyword arguments but does accept positional
        # arguments but we cannot use introspection on builtin function.
        code2 = 'globals({0})'
        good_code, bad_code1, bad_code2 = format_str(code2, '', '2', 'foo=2')
        self.runs(good_code)
        self.throws(bad_code1, NBARGERROR)
        self.throws(bad_code2, NBARGERROR, interpreters='pypy')
        self.throws(bad_code2, NOKWARGS, sugg, interpreters='cython')
        # The explanation is only relevant for C functions
        code3 = 'def func_no_arg(n):\n\tpass\nfunc_no_arg({0}2)'
        good_code, good_code2, bad_code = format_str(code3, '', 'n=', 'foo=')
        self.runs(good_code)
        self.runs(good_code2)
        self.throws(bad_code, UNEXPECTEDKWARG)

    def test_iter_cannot_be_interpreted_as_int(self):
        """Trying to call `range(len(iterable))` (bad) and forget the len."""
        before, after = before_and_after((3, 0))
        bad_code = 'range([0, 1, 2])'
        good_code = 'range(len([0, 1, 2]))'
        sugg = "'len(list)'"
        self.runs(good_code)
        self.throws(bad_code, INTEXPECTED, sugg, before)
        self.throws(bad_code, CANNOTBEINTERPRETED, sugg, after)

    RANGE_CODE_TEMPLATES = [
        'range({0})',
        'range({0}, 14)',
        'range(0, 24, {0})'
    ]
    INDEX_CODE_TEMPLATES = ['[1, 2, 3][{0}]', '(1, 2, 3)[{0}]']

    def test_str_cannot_be_interpreted_as_int(self):
        """Forget to convert str to int."""
        before, after = before_and_after((3, 0))
        suggs = ["'int(str)'", "'len(str)'"]
        for code in self.RANGE_CODE_TEMPLATES:
            bad_code, good_code = format_str(code, '"12"', 'int("12")')
            self.runs(good_code)
            self.throws(bad_code, INTEXPECTED, suggs, before)
            self.throws(bad_code, CANNOTBEINTERPRETED, suggs, after)

    def test_float_cannot_be_interpreted_as_int(self):
        """Use float instead of int."""
        before, mid, after = before_mid_and_after((2, 7), (3, 0))
        sugg = ["'int(float)'"]
        suggs = ["'int(float)'", "'math.ceil(float)'", "'math.floor(float)'"]
        for code in self.RANGE_CODE_TEMPLATES:
            full_code = 'import math\n' + code
            good1, good2, bad = format_str(
                full_code, 'int(12.0)', 'math.floor(12.0)', '12.0')
            self.runs(good1)
            self.runs(good2, before)
            # floor returns a float before Python 3 -_-
            self.throws(good2, INTEXPECTED, sugg, mid)
            self.runs(good2, after)
            self.runs(bad, before)
            self.throws(bad, INTEXPECTED, sugg, mid)
            self.throws(bad, CANNOTBEINTERPRETED, suggs, after)

    def test_customclass_cannot_be_interpreter_as_int(self):
        """Forget to implement the __index__ method."""
        # http://stackoverflow.com/questions/17342899/object-cannot-be-interpreted-as-an-integer
        # https://twitter.com/raymondh/status/773224135409360896
        before, after = before_and_after((3, 0))
        sugg = 'implement "__index__" on CustomClass'
        for code in self.RANGE_CODE_TEMPLATES:
            bad, good = format_str(code, 'CustomClass()', 'IndexClass()')
            self.throws(bad, ATTRIBUTEERROR, [], before)
            self.throws(bad, CANNOTBEINTERPRETED, sugg, after)
            self.runs(good, after)  # Fails on old python ?

    def test_indices_cant_be_str(self):
        """Use str as index."""
        suggs = ["'int(str)'", "'len(str)'"]
        for code in self.INDEX_CODE_TEMPLATES:
            bad, good = format_str(code, '"2"', 'int("2")')
            self.runs(good)
            self.throws(bad, INDICESMUSTBEINT, suggs)

    def test_indices_cant_be_float(self):
        """Use float as index."""
        before, after = before_and_after((3, 0))
        sugg = ["'int(float)'"]
        suggs = ["'int(float)'", "'math.ceil(float)'", "'math.floor(float)'"]
        for code in self.INDEX_CODE_TEMPLATES:
            good1, good2, bad = format_str(
                    code, 'int(2.0)', 'math.floor(2.0)', '2.0')
            self.runs(good1)
            # floor returns a float before Python 3 -_-
            self.throws(good2, INDICESMUSTBEINT, sugg, before)
            self.runs(good2, after)
            self.throws(bad, INDICESMUSTBEINT, sugg, before)
            self.throws(bad, INDICESMUSTBEINT, suggs, after)

    def test_indices_cant_be_custom(self):
        """Use custom as index."""
        before, after = before_and_after((3, 0))
        sugg = 'implement "__index__" on CustomClass'
        # On Pypy, detected type is 'instance' so attribute detection is much
        # less precise, leading to additional suggestions
        suggs = ["'len(instance)'", 'implement "__index__" on instance']
        for code in self.INDEX_CODE_TEMPLATES:
            bad, good = format_str(code, 'CustomClass()', 'IndexClass()')
            self.throws(bad, INDICESMUSTBEINT, suggs, before, 'pypy')
            self.throws(bad, CANNOTBEINTERPRETEDINDEX, [], before, 'cython')
            self.throws(bad, INDICESMUSTBEINT, sugg, after)
            self.runs(good)

    def test_no_implicit_str_conv(self):
        """Trying to concatenate a non-string value to a string."""
        # NICE_TO_HAVE
        code = '{0} + " things"'
        typo, good = '12', 'str(12)'
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, UNSUPPORTEDOPERAND)
        self.runs(good_code)

    def test_cannot_concatenate_iter_to_list(self):
        """Trying to concatenate a non-list iterable to a list."""
        # NICE_TO_HAVE
        before, after = before_and_after((3, 0))
        code = 'list() + {0}'
        good, bad, sugg, bad2, bad3, bad4 = \
            format_str(code, 'list()', 'set()', 'list(set())',
                       'range(10)', 'dict().keys()', 'dict().iterkeys()')
        self.runs(good)
        self.runs(sugg)
        self.throws(bad, ONLYCONCAT, interpreters='cython')
        self.throws(bad, UNSUPPORTEDOPERAND, interpreters='pypy')
        # Other examples are more interesting but depend on the version used:
        #  - range returns a list or a range object
        self.runs(bad2, before)
        self.throws(bad2, ONLYCONCAT, [], after, 'cython')
        self.throws(bad2, UNSUPPORTEDOPERAND, [], after, 'pypy')
        #  - keys return a list or a view object
        self.runs(bad3, before)
        self.throws(bad3, ONLYCONCAT, [], after, 'cython')
        self.throws(bad3, UNSUPPORTEDOPERAND, [], after, 'pypy')
        #  - iterkeys returns an iterator or doesn't exist
        self.throws(bad4, ONLYCONCAT, [], before, 'cython')
        self.throws(bad4, UNSUPPORTEDOPERAND, [], before, 'pypy')
        self.throws(bad4, ATTRIBUTEERROR, [], after)

    def test_no_implicit_str_conv2(self):
        """Trying to concatenate a non-string value to a string."""
        # NICE_TO_HAVE
        code = '"things " + {0}'
        typo, good = '12', 'str(12)'
        bad_code, good_code = format_str(code, typo, good)
        before, mid, after = before_mid_and_after((3, 0), (3, 6))
        self.throws(bad_code, CANNOTCONCAT, [], before, 'cython')
        self.throws(bad_code, CANTCONVERT, [], mid, 'cython')
        self.throws(bad_code, MUSTBETYPENOTTYPE, [], after, 'cython')
        self.throws(bad_code, UNSUPPORTEDOPERAND, interpreters='pypy')
        self.runs(good_code)

    def test_assignment_to_range(self):
        """Trying to assign to range works on list, not on range."""
        code = '{0}[2] = 1'
        typo, good = 'range(4)', 'list(range(4))'
        sugg = 'convert to list to edit the list'
        before, after = before_and_after((3, 0))
        bad_code, good_code = format_str(code, typo, good)
        self.runs(good_code)
        self.runs(bad_code, before)
        self.throws(bad_code, OBJECTDOESNOTSUPPORT, sugg, after)

    def test_assignment_to_string(self):
        """Trying to assign to string does not work."""
        code = "s = 'abc'\ns[1] = 'd'"
        good_code = "s = 'abc'\nl = list(s)\nl[1] = 'd'\ns = ''.join(l)"
        sugg = 'convert to list to edit the list and use "join()" on the list'
        self.runs(good_code)
        self.throws(code, OBJECTDOESNOTSUPPORT, sugg)

    def test_assignment_to_custom(self):
        """Trying to assign to custom obj."""
        before, after = before_and_after((3, 0))
        code = "o = {0}()\no[1] = 'd'"
        bad, good = format_str(code, 'CustomClass', 'SetItemClass')
        sugg = 'implement "__setitem__" on CustomClass'
        self.throws(bad, ATTRIBUTEERROR, [], before)
        self.throws(bad, OBJECTDOESNOTSUPPORT, sugg, after)
        self.runs(good)

    def test_deletion_from_string(self):
        """Delete from string does not work."""
        code = "s = 'abc'\ndel s[1]"
        good_code = "s = 'abc'\nl = list(s)\ndel l[1]\ns = ''.join(l)"
        sugg = 'convert to list to edit the list and use "join()" on the list'
        self.runs(good_code)
        self.throws(code, OBJECTDOESNOTSUPPORT, sugg)

    def test_deletion_from_custom(self):
        """Delete from custom obj does not work."""
        before, after = before_and_after((3, 0))
        code = "o = {0}()\ndel o[1]"
        bad, good = format_str(code, 'CustomClass', 'DelItemClass')
        sugg = 'implement "__delitem__" on CustomClass'
        self.throws(bad, ATTRIBUTEERROR, [], before)
        self.throws(bad, OBJECTDOESNOTSUPPORT, sugg, after)
        self.runs(good)

    def test_object_indexing(self):
        """Index from object does not work if __getitem__ is not defined."""
        before, after = before_and_after((3, 0))
        code = "{0}[0]"
        good_code, set_code, custom_bad, custom_good = \
            format_str(code, '"a_string"', "set()",
                       "CustomClass()", "GetItemClass()")
        self.runs(good_code)
        sugg_for_iterable = 'convert to list first or use the iterator ' \
            'protocol to get the different elements'
        sugg_imp = 'implement "__getitem__" on CustomClass'
        self.throws(set_code,
                    OBJECTDOESNOTSUPPORT,
                    sugg_for_iterable, interpreters='cython')
        self.throws(set_code,
                    UNSUBSCRIPTABLE,
                    sugg_for_iterable, interpreters='pypy')
        self.throws(custom_bad, ATTRIBUTEERROR, [], before, 'pypy')
        self.throws(custom_bad, UNSUBSCRIPTABLE, sugg_imp, after, 'pypy')
        self.throws(custom_bad, ATTRIBUTEERROR, [], before, 'cython')
        self.throws(custom_bad,
                    OBJECTDOESNOTSUPPORT,
                    sugg_imp,
                    after, 'cython')
        self.runs(custom_good)

    def test_not_callable(self):
        """Sometimes, one uses parenthesis instead of brackets."""
        typo, getitem = '(0)', '[0]'
        for ex, sugg in {
            '[0]': "'list[value]'",
            '{0: 0}': "'dict[value]'",
            '"a"': "'str[value]'",
        }.items():
            self.throws(ex + typo, NOTCALLABLE, sugg)
            self.runs(ex + getitem)
        for ex in ['1', 'set()']:
            self.throws(ex + typo, NOTCALLABLE)

    def test_not_callable_custom(self):
        """One must define __call__ to call custom objects."""
        before, after = before_and_after((3, 0))
        code = 'o = {0}()\no()'
        bad, good = format_str(code, 'CustomClass', 'CallClass')
        sugg = 'implement "__call__" on CustomClass'
        self.throws(bad, INSTHASNOMETH, [], before, 'cython')
        self.throws(bad, ATTRIBUTEERROR, [], before, 'pypy')
        self.throws(bad, NOTCALLABLE, sugg, after)
        self.runs(good)

    def test_exc_must_derive_from(self):
        """Test when a non-exc object is raised."""
        code = 'raise "ExceptionString"'
        self.throws(code, EXCMUSTDERIVE)

    def test_unordered_builtin(self):
        """Test for UNORDERABLE exception on builtin types."""
        before, mid, after = before_mid_and_after((3, 0), (3, 6))
        for op in ['>', '>=', '<', '<=']:
            code = "'10' {0} 2".format(op)
            self.runs(code, before)
            self.throws(code, UNORDERABLE, [], mid)
            self.throws(code, OPNOTSUPPBETWEENINST, [], after)

    def test_unordered_custom(self):
        """Test for UNORDERABLE exception on custom types."""
        before, mid, after = before_mid_and_after((3, 0), (3, 6))
        for op in ['>', '>=', '<', '<=']:
            code = "CustomClass() {0} CustomClass()".format(op)
            self.runs(code, before)
            self.throws(code, UNORDERABLE, [], mid)
            self.throws(code, OPNOTSUPPBETWEENINST, [], after)

    def test_unordered_custom2(self):
        """Test for UNORDERABLE exception on custom types."""
        before, mid, after = before_mid_and_after((3, 0), (3, 6))
        for op in ['>', '>=', '<', '<=']:
            code = "CustomClass() {0} 2".format(op)
            self.runs(code, before)
            self.throws(code, UNORDERABLE, [], mid)
            self.throws(code, OPNOTSUPPBETWEENINST, [], after)

    def test_unmatched_msg(self):
        """Test that arbitrary strings are supported."""
        code = 'raise TypeError("unmatched TYPEERROR")'
        self.throws(code, UNKNOWN_TYPEERROR)


class ImportErrorTests(GetSuggestionsTests):
    """Class for tests related to ImportError."""

    def test_no_module_no_sugg(self):
        """No suggestion."""
        self.throws('import fqslkdfjslkqdjfqsd', NOMODULE)

    def test_no_module(self):
        """Should be 'math'."""
        code = 'import {0}'
        typo, good = 'maths', 'math'
        self.assertTrue(good in STAND_MODULES)
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, NOMODULE, sugg)
        self.runs(good_code)

    def test_no_module2(self):
        """Should be 'math'."""
        code = 'from {0} import pi'
        typo, good = 'maths', 'math'
        self.assertTrue(good in STAND_MODULES)
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, NOMODULE, sugg)
        self.runs(good_code)

    def test_no_module3(self):
        """Should be 'math'."""
        code = 'import {0} as my_imported_math'
        typo, good = 'maths', 'math'
        self.assertTrue(good in STAND_MODULES)
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, NOMODULE, sugg)
        self.runs(good_code)

    def test_no_module4(self):
        """Should be 'math'."""
        code = 'from {0} import pi as three_something'
        typo, good = 'maths', 'math'
        self.assertTrue(good in STAND_MODULES)
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, NOMODULE, sugg)
        self.runs(good_code)

    def test_no_module5(self):
        """Should be 'math'."""
        code = '__import__("{0}")'
        typo, good = 'maths', 'math'
        self.assertTrue(good in STAND_MODULES)
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, NOMODULE, sugg)
        self.runs(good_code)

    def test_import_future_nomodule(self):
        """Should be '__future__'."""
        code = 'import {0}'
        typo, good = '__future_', '__future__'
        self.assertTrue(good in STAND_MODULES)
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, NOMODULE, sugg)
        self.runs(good_code)

    def test_no_name_no_sugg(self):
        """No suggestion."""
        self.throws('from math import fsfsdfdjlkf', CANNOTIMPORT)

    def test_wrong_import(self):
        """Should be 'math'."""
        code = 'from {0} import pi'
        typo, good = 'itertools', 'math'
        self.assertTrue(good in STAND_MODULES)
        bad_code, good_code = format_str(code, typo, good)
        sugg = "'{0}'".format(good_code)
        self.throws(bad_code, CANNOTIMPORT, sugg)
        self.runs(good_code)

    def test_typo_in_method(self):
        """Should be 'pi'."""
        code = 'from math import {0}'
        typo, good = 'pie', 'pi'
        sugg = quote(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, CANNOTIMPORT, sugg)
        self.runs(good_code)

    def test_typo_in_method2(self):
        """Should be 'pi'."""
        code = 'from math import e, {0}, log'
        typo, good = 'pie', 'pi'
        sugg = quote(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, CANNOTIMPORT, sugg)
        self.runs(good_code)

    def test_typo_in_method3(self):
        """Should be 'pi'."""
        code = 'from math import {0} as three_something'
        typo, good = 'pie', 'pi'
        sugg = quote(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, CANNOTIMPORT, sugg)
        self.runs(good_code)

    def test_unmatched_msg(self):
        """Test that arbitrary strings are supported."""
        code = 'raise ImportError("unmatched IMPORTERROR")'
        self.throws(code, UNKNOWN_IMPORTERROR)

    def test_module_removed(self):
        """Sometimes, modules are deleted/moved/renamed."""
        # NICE_TO_HAVE
        # result for 2.6 seems to vary
        _, mid, after = before_mid_and_after((2, 7), (3, 0))
        code = 'import {0}'
        lower, upper = format_str(code, 'tkinter', 'Tkinter')
        self.throws(lower, NOMODULE, [], mid)
        self.throws(upper, NOMODULE, [], after)


class LookupErrorTests(GetSuggestionsTests):
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


class SyntaxErrorTests(GetSuggestionsTests):
    """Class for tests related to SyntaxError."""

    def test_no_error(self):
        """No error."""
        self.runs("1 + 2 == 2")

    def test_yield_return_out_of_func(self):
        """yield/return needs to be in functions."""
        sugg = "to indent it"
        self.throws("yield 1", OUTSIDEFUNC, sugg)
        self.throws("return 1", OUTSIDEFUNC, ["'sys.exit([arg])'", sugg])

    def test_print(self):
        """print is a function now and needs parenthesis."""
        # NICE_TO_HAVE
        code, new_code = 'print ""', 'print("")'
        before, after = before_and_after((3, 0))
        self.runs(code, before)
        self.throws(code, INVALIDSYNTAX, [], after)
        self.runs(new_code)

    def test_exec(self):
        """exec is a function now and needs parenthesis."""
        # NICE_TO_HAVE
        code, new_code = 'exec "1"', 'exec("1")'
        before, after = before_and_after((3, 0))
        self.runs(code, before)
        self.throws(code, INVALIDSYNTAX, [], after)
        self.runs(new_code)

    def test_old_comparison(self):
        """<> comparison is removed, != always works."""
        code = '1 {0} 2'
        old, new = '<>', '!='
        sugg = "'{0}'".format(new)
        before, after = before_and_after((3, 0))
        old_code, new_code = format_str(code, old, new)
        self.runs(old_code, before)
        self.throws(old_code, INVALIDCOMP, sugg, after, 'pypy')
        self.throws(old_code, INVALIDSYNTAX, sugg, after, 'cython')
        self.runs(new_code)

    def test_backticks(self):
        """String with backticks is removed in Python3, use 'repr' instead."""
        # NICE_TO_HAVE
        before, after = before_and_after((3, 0))
        expr = "2+3"
        backtick_str, repr_str = "`%s`" % expr, "repr(%s)" % expr
        self.runs(backtick_str, before)
        self.throws(backtick_str, INVALIDSYNTAX, [], after)
        self.runs(repr_str)

    def test_missing_colon(self):
        """Missing colon is a classic mistake."""
        # NICE_TO_HAVE
        code = "if True{0}\n\tpass"
        bad_code, good_code = format_str(code, "", ":")
        self.throws(bad_code, INVALIDSYNTAX)
        self.runs(good_code)

    def test_missing_colon2(self):
        """Missing colon is a classic mistake."""
        # NICE_TO_HAVE
        code = "class MyClass{0}\n\tpass"
        bad_code, good_code = format_str(code, "", ":")
        self.throws(bad_code, INVALIDSYNTAX)
        self.runs(good_code)

    def test_simple_equal(self):
        """'=' for comparison is a classic mistake."""
        # NICE_TO_HAVE
        code = "if 2 {0} 3:\n\tpass"
        bad_code, good_code = format_str(code, "=", "==")
        self.throws(bad_code, INVALIDSYNTAX)
        self.runs(good_code)

    def test_keyword_as_identifier(self):
        """Using a keyword as a variable name."""
        # NICE_TO_HAVE
        code = '{0} = 1'
        bad_code, good_code = format_str(code, "from", "from_")
        self.throws(bad_code, INVALIDSYNTAX)
        self.runs(good_code)

    def test_increment(self):
        """Trying to use '++' or '--'."""
        # NICE_TO_HAVE
        code = 'a = 0\na{0}'
        # Adding pointless suffix to avoid wrong assumptions
        for end in ('', '  ', ';', ' ;'):
            code2 = code + end
            for op in ('-', '+'):
                typo, good = 2 * op, op + '=1'
                bad_code, good_code = format_str(code2, typo, good)
                self.throws(bad_code, INVALIDSYNTAX)
                self.runs(good_code)

    def test_wrong_bool_operator(self):
        """Trying to use '&&' or '||'."""
        code = 'True {0} False'
        for typo, good in (('&&', 'and'), ('||', 'or')):
            bad_code, good_code = format_str(code, typo, good)
            sugg = quote(good)
            self.throws(bad_code, INVALIDSYNTAX, sugg)
            self.runs(good_code)

    def test_import_future_not_first(self):
        """Test what happens when import from __future__ is not first."""
        code = 'a = 8/7\nfrom __future__ import division'
        self.throws(code, FUTUREFIRST)

    def test_import_future_not_def(self):
        """Should be 'division'."""
        code = 'from __future__ import {0}'
        typo, good = 'divisio', 'division'
        bad_code, good_code = format_str(code, typo, good)
        sugg = quote(good)
        self.throws(bad_code, FUTFEATNOTDEF, sugg)
        self.runs(good_code)

    def test_unqualified_exec(self):
        """Exec in nested functions."""
        # NICE_TO_HAVE
        before, after = before_and_after((3, 0))
        codes = [
            "def func1():\n\tbar='1'\n\tdef func2():"
            "\n\t\texec(bar)\n\tfunc2()\nfunc1()",
            "def func1():\n\texec('1')\n\tdef func2():"
            "\n\t\tTrue",
        ]
        for code in codes:
            self.throws(code, UNQUALIFIED_EXEC, [], before)
            self.runs(code, after)

    def test_import_star(self):
        """'import *' in nested functions."""
        # NICE_TO_HAVE
        codes = [
            "def func1():\n\tbar='1'\n\tdef func2():"
            "\n\t\tfrom math import *\n\t\tTrue\n\tfunc2()\nfunc1()",
            "def func1():\n\tfrom math import *"
            "\n\tdef func2():\n\t\tTrue",
        ]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=SyntaxWarning)
            for code in codes:
                self.throws(code, IMPORTSTAR)

    def test_unpack(self):
        """Extended tuple unpacking does not work prior to Python 3."""
        # NICE_TO_HAVE
        before, after = before_and_after((3, 0))
        code = 'a, *b = (1, 2, 3)'
        self.throws(code, INVALIDSYNTAX, [], before)
        self.runs(code, after)

    def test_unpack2(self):
        """Unpacking in function arguments was supported up to Python 3."""
        # NICE_TO_HAVE
        before, after = before_and_after((3, 0))
        code = 'def addpoints((x1, y1), (x2, y2)):\n\tpass'
        self.runs(code, before)
        self.throws(code, INVALIDSYNTAX, [], after)

    def test_nonlocal(self):
        """nonlocal keyword is added in Python 3."""
        # NICE_TO_HAVE
        before, after = before_and_after((3, 0))
        code = 'def func():\n\tfoo = 1\n\tdef nested():\n\t\tnonlocal foo'
        self.throws(code, INVALIDSYNTAX, [], before)
        self.runs(code, after)

    def test_nonlocal2(self):
        """nonlocal must be used only when binding exists."""
        # NICE_TO_HAVE
        before, after = before_and_after((3, 0))
        code = 'def func():\n\tdef nested():\n\t\tnonlocal foo'
        self.throws(code, INVALIDSYNTAX, [], before)
        self.throws(code, NOBINDING, [], after)

    def test_nonlocal3(self):
        """nonlocal must be used only when binding to non-global exists."""
        # just a way to say that this_is_a_global_list is needed in globals
        name = 'this_is_a_global_list'
        this_is_a_global_list
        self.assertFalse(name in locals())
        self.assertTrue(name in globals())
        before, after = before_and_after((3, 0))
        code = 'def func():\n\tdef nested():\n\t\t{0} ' + name
        typo, good = 'nonlocal', 'global'
        sugg = "'{0} {1}'".format(good, name)
        bad_code, good_code = format_str(code, typo, good)
        self.runs(good_code)
        self.throws(bad_code, INVALIDSYNTAX, [], before)
        self.throws(bad_code, NOBINDING, sugg, after)

    def test_nonlocal4(self):
        """suggest close matches to variable name."""
        # NICE_TO_HAVE (needs access to variable in enclosing scope)
        before, after = before_and_after((3, 0))
        code = 'def func():\n\tfoo = 1\n\tdef nested():\n\t\tnonlocal {0}'
        typo, good = 'foob', 'foo'
        bad_code, good_code = format_str(code, typo, good)
        self.throws(good_code, INVALIDSYNTAX, [], before)
        self.runs(good_code, after)
        self.throws(bad_code, INVALIDSYNTAX, [], before)
        self.throws(bad_code, NOBINDING, [], after)

    def test_nonlocal_at_module_level(self):
        """nonlocal must be used in function."""
        before, mid, after = before_mid_and_after((2, 7), (3, 0))
        code = 'nonlocal foo'
        self.throws(code, UNEXPECTED_OEF, [], before)
        self.throws(code, INVALIDSYNTAX, [], mid)
        self.throws(code, NONLOCALMODULE, [], after)

    def test_octal_literal(self):
        """Syntax for octal liberals has changed."""
        # NICE_TO_HAVE
        before, after = before_and_after((3, 0))
        bad, good = '0720', '0o720'
        self.runs(good)
        self.runs(bad, before)
        self.throws(bad, INVALIDTOKEN, [], after, 'cython')
        self.throws(bad, INVALIDSYNTAX, [], after, 'pypy')

    def test_extended_unpacking(self):
        """Extended iterable unpacking is added with Python 3."""
        before, after = before_and_after((3, 0))
        code = '(a, *rest, b) = range(5)'
        self.throws(code, INVALIDSYNTAX, [], before)
        self.runs(code, after)

    def test_ellipsis(self):
        """Triple dot (...) aka Ellipsis can be used anywhere in Python 3."""
        before, after = before_and_after((3, 0))
        code = '...'
        self.throws(code, INVALIDSYNTAX, [], before)
        self.runs(code, after)

    def test_fstring(self):
        """Fstring (see PEP 498) appeared in Python 3.6."""
        # NICE_TO_HAVE
        before, after = before_and_after((3, 6))
        code = 'f"toto"'
        self.throws(code, INVALIDSYNTAX, [], before)
        self.runs(code, after)


class MemoryErrorTests(GetSuggestionsTests):
    """Class for tests related to MemoryError."""

    def test_out_of_memory(self):
        """Test what happens in case of MemoryError."""
        code = '[0] * 999999999999999'
        self.throws(code, MEMORYERROR)

    def test_out_of_memory_range(self):
        """Test what happens in case of MemoryError."""
        code = '{0}(999999999999999)'
        typo, good = 'range', 'xrange'
        sugg = quote(good)
        bad_code, good_code = format_str(code, typo, good)
        before, mid, after = before_mid_and_after((2, 7), (3, 0))
        self.runs(bad_code, interpreters='pypy')
        self.throws(bad_code, OVERFLOWERR, sugg, before, 'cython')
        self.throws(bad_code, MEMORYERROR, sugg, mid, 'cython')
        self.runs(bad_code, after, 'cython')
        self.runs(good_code, before, 'cython')
        self.runs(good_code, mid, 'cython')


class ValueErrorTests(GetSuggestionsTests):
    """Class for tests related to ValueError."""

    def test_too_many_values(self):
        """Unpack 4 values in 3 variables."""
        code = 'a, b, c = [1, 2, 3, 4]'
        before, after = before_and_after((3, 0))
        self.throws(code, EXPECTEDLENGTH, [], before, 'pypy')
        self.throws(code, TOOMANYVALUES, [], after, 'pypy')
        self.throws(code, TOOMANYVALUES, interpreters='cython')

    def test_not_enough_values(self):
        """Unpack 2 values in 3 variables."""
        code = 'a, b, c = [1, 2]'
        before, after = before_and_after((3, 0))
        self.throws(code, EXPECTEDLENGTH, [], before, 'pypy')
        self.throws(code, NEEDMOREVALUES, [], after, 'pypy')
        self.throws(code, NEEDMOREVALUES, interpreters='cython')

    def test_conversion_fails(self):
        """Conversion fails."""
        self.throws('int("toto")', INVALIDLITERAL)

    def test_math_domain(self):
        """Math function used out of its domain."""
        code = 'import math\nlg = math.log(-1)'
        self.throws(code, MATHDOMAIN)

    def test_zero_len_field_in_format(self):
        """Format {} is not valid before Python 2.7."""
        code = '"{0}".format(0)'
        old, new = '{0}', '{}'
        old_code, new_code = format_str(code, old, new)
        before, after = before_and_after((2, 7))
        self.runs(old_code)
        self.throws(new_code, ZEROLENERROR, '{0}', before)
        self.runs(new_code, after)

    def test_timedata_does_not_match(self):
        """Strptime arguments are in wrong order."""
        # https://twitter.com/brandon_rhodes/status/781234730091941888
        code = 'import datetime\ndatetime.datetime.strptime({0}, {1})'
        timedata, timeformat = '"30 Nov 00"', '"%d %b %y"'
        good_code = code.format(*(timedata, timeformat))
        bad_code = code.format(*(timeformat, timedata))
        sugg = 'to swap value and format parameters'
        self.runs(good_code)
        self.throws(bad_code, TIMEDATAFORMAT, sugg)


class RuntimeErrorTests(GetSuggestionsTests):
    """Class for tests related to RuntimeError."""

    def test_max_depth(self):
        """Reach maximum recursion depth."""
        original_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(200)
        code = 'endlessly_recursive_func(0)'
        suggs = ["increase the limit with `sys.setrecursionlimit(limit)`"
                 " (current value is 200)", AVOID_REC_MSG]
        self.throws(code, MAXRECURDEPTH, suggs)
        sys.setrecursionlimit(original_limit)

    def test_dict_size_changed_during_iter(self):
        """Test size change during iteration (dict)."""
        # NICE_TO_HAVE
        code = 'd = dict(enumerate("notimportant"))' \
            '\nfor e in d:\n\td.pop(e)'
        self.throws(code, SIZECHANGEDDURINGITER)

    def test_set_changed_size_during_iter(self):
        """Test size change during iteration (set)."""
        # NICE_TO_HAVE
        code = 's = set("notimportant")' \
            '\nfor e in s:\n\ts.pop()'
        self.throws(code, SIZECHANGEDDURINGITER)

    def test_dequeue_changed_during_iter(self):
        """Test size change during iteration (dequeue)."""
        # NICE_TO_HAVE
        # "deque mutated during iteration"
        pass


class IOErrorTests(GetSuggestionsTests):
    """Class for tests related to IOError."""

    def test_no_such_file(self):
        """File does not exist."""
        code = 'with open("doesnotexist") as f:\n\tpass'
        self.throws(code, NOFILE_IO)

    def test_no_such_file2(self):
        """File does not exist."""
        code = 'os.listdir("doesnotexist")'
        self.throws(code, NOFILE_OS)

    def test_no_such_file_user(self):
        """Suggestion when one needs to expanduser."""
        code = 'os.listdir("{0}")'
        typo, good = "~", os.path.expanduser("~")
        sugg = "'{0}' (calling os.path.expanduser)".format(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NOFILE_OS, sugg)
        self.runs(good_code)

    def test_no_such_file_vars(self):
        """Suggestion when one needs to expandvars."""
        code = 'os.listdir("{0}")'
        key = 'HOME'
        typo, good = "$" + key, os.path.expanduser("~")
        original_home = os.environ.get('HOME')
        os.environ[key] = good
        bad_code, good_code = format_str(code, typo, good)
        sugg = "'{0}' (calling os.path.expandvars)".format(good)
        self.throws(bad_code, NOFILE_OS, sugg)
        self.runs(good_code)
        if original_home is None:
            del os.environ[key]
        else:
            os.environ[key] = original_home

    def create_tmp_dir_with_files(self, filelist):
        """Create a temporary directory with files in it."""
        tmpdir = tempfile.mkdtemp()
        absfiles = [os.path.join(tmpdir, f) for f in filelist]
        for name in absfiles:
            open(name, 'a').close()
        return (tmpdir, absfiles)

    def test_is_dir_empty(self):
        """Suggestion when file is an empty directory."""
        # Create empty temp dir
        tmpdir, _ = self.create_tmp_dir_with_files([])
        code = 'with open("{0}") as f:\n\tpass'
        bad_code, _ = format_str(code, tmpdir, "TODO")
        sugg = "to add content to {0} first".format(tmpdir)
        self.throws(bad_code, ISADIR_IO, sugg)
        rmtree(tmpdir)

    def test_is_dir_small(self):
        """Suggestion when file is directory with a few files."""
        # Create temp dir with a few files
        nb_files = 3
        files = sorted([str(i) + ".txt" for i in range(nb_files)])
        tmpdir, absfiles = self.create_tmp_dir_with_files(files)
        code = 'with open("{0}") as f:\n\tpass'
        bad_code, good_code = format_str(code, tmpdir, absfiles[0])
        suggs = "any of the 3 files in directory ('0.txt', '1.txt', '2.txt')"
        self.throws(bad_code, ISADIR_IO, suggs)
        self.runs(good_code)
        rmtree(tmpdir)

    def test_is_dir_big(self):
        """Suggestion when file is directory with many files."""
        # Create temp dir with many files
        tmpdir = tempfile.mkdtemp()
        nb_files = 30
        files = sorted([str(i) + ".txt" for i in range(nb_files)])
        tmpdir, absfiles = self.create_tmp_dir_with_files(files)
        code = 'with open("{0}") as f:\n\tpass'
        bad_code, good_code = format_str(code, tmpdir, absfiles[0])
        suggs = "any of the 30 files in directory " \
            "('0.txt', '1.txt', '10.txt', '11.txt', etc)"
        self.throws(bad_code, ISADIR_IO, suggs)
        self.runs(good_code)
        rmtree(tmpdir)

    def test_is_not_dir(self):
        """Suggestion when file is not a directory."""
        code = 'with open("{0}") as f:\n\tpass'
        code = 'os.listdir("{0}")'
        typo, good = __file__, os.path.dirname(__file__)
        sugg = "'{0}' (calling os.path.dirname)".format(good)
        bad_code, good_code = format_str(code, typo, good)
        self.throws(bad_code, NOTADIR_OS, sugg)
        self.runs(good_code)

    def test_dir_is_not_empty(self):
        """Suggestion when directory is not empty."""
        # NICE_TO_HAVE
        nb_files = 3
        files = sorted([str(i) + ".txt" for i in range(nb_files)])
        tmpdir, _ = self.create_tmp_dir_with_files(files)
        self.throws('os.rmdir("{0}")'.format(tmpdir), DIRNOTEMPTY_OS)
        rmtree(tmpdir)  # this should be the suggestion


class AnyErrorTests(GetSuggestionsTests):
    """Class for tests not related to an error type in particular."""

    def test_wrong_except(self):
        """Test where except is badly used and thus does not catch.

        Common mistake : "except Exc1, Exc2" doesn't catch Exc2.
        Adding parenthesis solves the issue.
        """
        # NICE_TO_HAVE
        before, after = before_and_after((3, 0))
        raised_exc, other_exc = KeyError, TypeError
        raised, other = raised_exc.__name__, other_exc.__name__
        code = "try:\n\traise {0}()\nexcept {{0}}:\n\tpass".format(raised)
        typo = "{0}, {1}".format(other, raised)
        sugg = "({0})".format(typo)
        bad1, bad2, good1, good2 = format_str(code, typo, other, sugg, raised)
        self.throws(bad1, (raised_exc, None), [], before)
        self.throws(bad1, INVALIDSYNTAX, [], after)
        self.throws(bad2, (raised_exc, None))
        self.runs(good1)
        self.runs(good2)


if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
