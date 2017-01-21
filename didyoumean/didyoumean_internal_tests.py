# -*- coding: utf-8
"""Unit tests for code in didyoumean_internal.py."""
from didyoumean_internal import get_suggestion_string,\
    add_string_to_exception, get_func_by_name,\
    get_objects_in_frame, get_subclasses, get_types_for_str,\
    get_types_for_str_using_inheritance,\
    get_types_for_str_using_names
import didyoumean_common_tests as common
from didyoumean_common_tests import CommonTestOldStyleClass2,\
    CommonTestNewStyleClass2  # to have these 2 in defined names
import unittest2
import itertools
import sys


OLD_CLASS_SUPPORT = sys.version_info >= (3, 0)
IS_PYPY = hasattr(sys, "pypy_translation_info")
U_PREFIX_SUPPORT = not ((3, 0) <= sys.version_info < (3, 3))
U_PREFIX = "u" if U_PREFIX_SUPPORT else ""
global_var = 42  # Please don't change the value


class QuoteTests(unittest2.TestCase):
    """Class for tests related to quote."""

    def quote_empty_str(self):
        """Test quote on empty string."""
        self.assertEqual(quote(''), "''")

    def quote_str(self):
        """Test quote on non-empty string."""
        self.assertEqual(quote('abc'), "'abc'")


class GetObjectInFrameTests(unittest2.TestCase):
    """Class for tests related to frame/backtrace/etc inspection.

    Tested functions are : get_objects_in_frame.
    No tests about 'nonlocal' is written because it is only supported
    from Python 3.
    """

    def name_corresponds_to(self, name, expected):
        """Helper functions to test get_objects_in_frame.

        Check that the name corresponds to the expected objects (and their
        scope) in the frame of calling function.
        None can be used to match any object as it can be hard to describe
        an object when it is hidden by something in a closer scope.
        Also, extra care is to be taken when calling the function because
        giving value by names might affect the result (adding in local
        scope).
        """
        frame = sys._getframe(1)  # frame of calling function
        lst = get_objects_in_frame(frame).get(name, [])
        self.assertEqual(len(lst), len(expected))
        for scopedobj, exp in zip(lst, expected):
            obj, scope = scopedobj
            expobj, expscope = exp
            self.assertEqual(scope, expscope, name)
            if expobj is not None:
                self.assertEqual(obj, expobj, name)

    def test_builtin(self):
        """Test with builtin."""
        builtin = len
        name = builtin.__name__
        self.name_corresponds_to(name, [(builtin, 'builtin')])

    def test_builtin2(self):
        """Test with builtin."""
        name = 'True'
        self.name_corresponds_to(name, [(bool(1), 'builtin')])

    def test_global(self):
        """Test with global."""
        name = 'global_var'
        self.name_corresponds_to(name, [(42, 'global')])

    def test_local(self):
        """Test with local."""
        name = 'toto'
        self.name_corresponds_to(name, [])
        toto = 0
        self.name_corresponds_to(name, [(0, 'local')])

    def test_local_and_global(self):
        """Test with local hiding a global."""
        name = 'global_var'
        self.name_corresponds_to(name, [(42, 'global')])
        global_var = 1
        self.name_corresponds_to(name, [(1, 'local'), (42, 'global')])

    def test_global_keword(self):
        """Test with global keyword."""
        # Funny detail : the global keyword works even if at the end of
        # the function (after the code it affects) but this raises a
        # SyntaxWarning.
        global global_var
        name = 'global_var'
        global_var = 42  # value is unchanged
        self.name_corresponds_to(name, [(42, 'global')])

    def test_del_local(self):
        """Test with deleted local."""
        name = 'toto'
        self.name_corresponds_to(name, [])
        toto = 0
        self.name_corresponds_to(name, [(0, 'local')])
        del toto
        self.name_corresponds_to(name, [])

    def test_del_local_hiding_global(self):
        """Test with deleted local hiding a global."""
        name = 'global_var'
        glob_desc = [(42, 'global')]
        local_desc = [(1, 'local')]
        self.name_corresponds_to(name, glob_desc)
        global_var = 1
        self.name_corresponds_to(name, local_desc + glob_desc)
        del global_var
        self.name_corresponds_to(name, glob_desc)

    def test_enclosing(self):
        """Test with nested functions."""
        foo = 1
        bar = 2

        def nested_func(foo, baz):
            qux = 5
            self.name_corresponds_to('qux', [(5, 'local')])
            self.name_corresponds_to('baz', [(4, 'local')])
            self.name_corresponds_to('foo', [(3, 'local')])
            self.name_corresponds_to('bar', [])
            self.name_corresponds_to(
                'global_var', [(42, 'global')])
        nested_func(3, 4)
        self.name_corresponds_to('nested_func', [(nested_func, 'local')])
        self.name_corresponds_to('foo', [(1, 'local')])
        self.name_corresponds_to('baz', [])

    def test_enclosing2(self):
        """Test with nested functions."""
        bar = 2

        def nested_func():
            self.name_corresponds_to('bar', [])
            bar = 3
            self.name_corresponds_to('bar', [(3, 'local')])

        nested_func()
        self.name_corresponds_to('nested_func', [(nested_func, 'local')])

    def test_enclosing3(self):
        """Test with nested functions."""
        bar = 2

        def nested_func():
            self.name_corresponds_to('bar', [(2, 'local')])
            tmp = bar
            self.name_corresponds_to('bar', [(2, 'local')])

        nested_func()
        self.name_corresponds_to('nested_func', [(nested_func, 'local')])

    def test_enclosing4(self):
        """Test with nested functions."""
        global_var = 1

        def nested_func():
            self.name_corresponds_to('global_var', [(42, 'global')])

        nested_func()
        self.name_corresponds_to('global_var', [(1, 'local'), (42, 'global')])

    def test_enclosing5(self):
        """Test with nested functions."""
        bar = 2
        foo = 3

        def nested_func():
            bar = 4
            baz = 5
            self.name_corresponds_to('foo', [])
            self.name_corresponds_to('bar', [(4, 'local')])

            def nested_func2():
                self.name_corresponds_to('foo', [])
                self.name_corresponds_to('bar', [])

            nested_func2()

        nested_func()
        self.name_corresponds_to('nested_func', [(nested_func, 'local')])


class OldStyleBaseClass:
    """Dummy class for testing purposes."""

    pass


class OldStyleDerivedClass(OldStyleBaseClass):
    """Dummy class for testing purposes."""

    pass


class NewStyleBaseClass(object):
    """Dummy class for testing purposes."""

    pass


class NewStyleDerivedClass(NewStyleBaseClass):
    """Dummy class for testing purposes."""

    pass


def a_function():
    """Dummy function for testing purposes."""
    pass


def a_generator():
    """Dummy generator for testing purposes."""
    yield 1


NEW_STYLE_CLASSES = [bool, int, float, str, tuple, list, set, dict, object,
                     NewStyleBaseClass, NewStyleDerivedClass,
                     common.CommonTestNewStyleClass,
                     common.CommonTestNewStyleClass2,
                     type(a_function), type(a_generator),
                     type(len), type(None), type(type(None)),
                     type(object), type(sys), type(range),
                     type(NewStyleBaseClass), type(NewStyleDerivedClass),
                     type(OldStyleBaseClass), type(OldStyleDerivedClass)]
OLD_STYLE_CLASSES = [OldStyleBaseClass, OldStyleDerivedClass,
                     CommonTestOldStyleClass2]
CLASSES = [(c, True) for c in NEW_STYLE_CLASSES] + \
    [(c, False) for c in OLD_STYLE_CLASSES]


class GetTypesForStrTests(unittest2.TestCase):
    """Test get_types_for_str."""

    def test_get_subclasses(self):
        """Test the get_subclasses function.

        All types are found when looking for subclasses of object, except
        for the old style classes on Python 2.x.
        """
        all_classes = get_subclasses(object)
        for typ, new in CLASSES:
            self.assertTrue(typ in get_subclasses(typ))
            if new or OLD_CLASS_SUPPORT:
                self.assertTrue(typ in all_classes)
            else:
                self.assertFalse(typ in all_classes)
        self.assertFalse(0 in all_classes)

    def test_get_types_for_str_using_inheritance(self):
        """Test the get_types_for_str_using_inheritance function.

        All types are found when looking for subclasses of object, except
        for the old style classes on Python 2.x.

        Also, it seems like the returns is (almost) always precise as the
        returned set contains only the expected type and nothing else.
        """
        for typ, new in CLASSES:
            types = get_types_for_str_using_inheritance(typ.__name__)
            if new or OLD_CLASS_SUPPORT:
                self.assertEqual(types, set([typ]), typ)
            else:
                self.assertEqual(types, set(), typ)

        self.assertFalse(get_types_for_str_using_inheritance('faketype'))

    def get_types_using_names(self, type_str):
        """Wrapper around the get_types_using_names function."""
        return get_types_for_str_using_names(type_str, sys._getframe(1))

    def test_get_types_for_str_using_names(self):
        """Test the get_types_using_names function.

        Old style classes are retrieved even on Python 2.x.
        However, a few builtin types are not in the names so can't be found.
        """
        for typ in OLD_STYLE_CLASSES:
            types = self.get_types_using_names(typ.__name__)
            self.assertEqual(types, set([typ]), typ)
        for n in ['generator', 'module', 'function', 'faketype']:
            self.assertEqual(self.get_types_using_names(n), set(), n)
        n = 'NoneType'
        if IS_PYPY:
            self.assertEqual(len(self.get_types_using_names(n)), 1, n)
        else:
            self.assertEqual(self.get_types_using_names(n), set(), n)

    def get_types_for_str(self, type_str):
        """Wrapper around the get_types_for_str function."""
        return get_types_for_str(type_str, sys._getframe(1))

    def test_get_types_for_str(self):
        """Test the get_types_for_str function.

        Check that for all tested types, the proper type is retrieved.
        """
        for typ, _ in CLASSES:
            types = self.get_types_for_str(typ.__name__)
            self.assertEqual(types, set([typ]), typ)

        self.assertEqual(self.get_types_for_str('faketype'), set())

    def test_get_types_for_str2(self):
        """Test the get_types_for_str function.

        Check that for all tested strings, a single type is retrived.
        This is useful to ensure that we are using the right names.
        """
        for n in ['module', 'NoneType', 'function',
                  'NewStyleBaseClass', 'NewStyleDerivedClass',
                  'OldStyleBaseClass', 'OldStyleDerivedClass']:
            types = self.get_types_for_str(n)
            self.assertEqual(len(types), 1, n)
        for n in ['generator']:  # FIXME: with pypy, we find an additional type
            types = self.get_types_for_str(n)
            self.assertEqual(len(types), 2 if IS_PYPY else 1, n)

    def test_old_class_not_in_namespace(self):
        """Test the get_types_for_str function.

        Check that at the moment, CommonTestOldStyleClass is not found
        because it is not in the namespace. This behavior is to be improved.
        """
        typ = common.CommonTestOldStyleClass
        expect_with_inherit = set([typ]) if OLD_CLASS_SUPPORT else set()
        name = typ.__name__
        types1 = get_types_for_str_using_inheritance(name)
        types2 = self.get_types_using_names(name)
        types3 = self.get_types_for_str(name)
        self.assertEqual(types1, expect_with_inherit)
        self.assertEqual(types2, set())
        self.assertEqual(types3, expect_with_inherit)


class GetFuncByNameTests(unittest2.TestCase):
    """Test get_func_by_name."""

    def get_func_by_name(self, func_name):
        """Wrapper around the get_func_by_name function."""
        return get_func_by_name(func_name, sys._getframe(1))

    def check_get_func_by_name(self, function, exact_match=True):
        """Wrapper around the get_func_by_name to check its result."""
        self.assertTrue(hasattr(function, '__name__'), function)
        res = self.get_func_by_name(function.__name__)
        self.assertTrue(function in res)
        self.assertTrue(len(res) >= 1, res)
        if exact_match:
            # Equality above does not hold
            # Using set is complicated because everything can't be hashed
            # But using id, something seems to be possible
            self.assertEqual(len(set(res)), 1, res)
            res_ids = [id(e) for e in res]
            set_ids = set(res_ids)
            self.assertEqual(len(set_ids), 1, set_ids)

    def test_get_builtin_by_name(self):
        """Test get_func_by_name on builtin functions."""
        for f in [bool, int, float, str, tuple, list, set, dict, all]:
            self.check_get_func_by_name(f)
        for f in [object]:
            self.check_get_func_by_name(f, False)

    def test_get_builtin_attr_by_name(self):
        """Test get_func_by_name on builtin attributes."""
        for f in [dict.get]:
            self.check_get_func_by_name(f, False)

    def test_get_lambda_by_name(self):
        """Test get_func_by_name on lambda functions."""
        self.check_get_func_by_name(lambda x: x)

    def test_get_custom_func_by_name(self):
        """Test get_func_by_name on custom functions."""
        for f in [a_function, a_generator]:
            self.check_get_func_by_name(f)

    def test_get_class_func_by_name(self):
        """Test get_func_by_name on custom functions."""
        for f, new in CLASSES:
            self.check_get_func_by_name(f, False)

    def test_inexisting_func(self):
        """Test get_func_by_name on an inexisting function name."""
        self.assertEqual(self.get_func_by_name('dkalskjdas'), [])


class GetSuggStringTests(unittest2.TestCase):
    """Tests about get_suggestion_string."""

    def test_no_sugg(self):
        """Empty list of suggestions."""
        self.assertEqual(get_suggestion_string(()), "")

    def test_one_sugg(self):
        """Single suggestion."""
        self.assertEqual(get_suggestion_string(('0',)), ". Did you mean 0?")

    def test_same_sugg(self):
        """Identical suggestion."""
        self.assertEqual(
            get_suggestion_string(('0', '0')), ". Did you mean 0, 0?")

    def test_multiple_suggs(self):
        """Multiple suggestions."""
        self.assertEqual(
            get_suggestion_string(('0', '1')), ". Did you mean 0, 1?")


class AddStringToExcTest(common.TestWithStringFunction):
    """Generic class for tests about add_string_to_exception."""

    prefix_repr = ""
    suffix_repr = ""
    check_str_sum = True

    def get_exception(self):
        """Abstract method to get an instance of exception."""
        raise NotImplementedError("'get_exception' needs to be implemented")

    def get_exc_before_and_after(self, string, func):
        """Retrieve string representations of exceptions.

        Retrieve string representations of exceptions raised by code
        before and after calling add_string_to_exception.
        """
        value = self.get_exception()
        before = func(value)
        add_string_to_exception(value, string)
        after = func(value)
        return (before, after)

    def check_string_added(self, func, string, prefix="", suffix=""):
        """Check that add_string_to_exception adds the strings."""
        s1, s2 = self.get_exc_before_and_after(string, func)
        self.assertStringAdded(
            prefix + string + suffix, s1, s2, self.check_str_sum)

    def test_add_empty_string_to_str(self):
        """Empty string added to error's str value."""
        self.check_string_added(str, "")

    def test_add_empty_string_to_repr(self):
        """Empty string added to error's repr value."""
        self.check_string_added(repr, "")

    def test_add_string_to_str(self):
        """Non-empty string added to error's str value."""
        self.check_string_added(str, "ABCDEstr")

    def test_add_string_to_repr(self):
        """Non-empty string added to error's repr value."""
        self.check_string_added(
            repr, "ABCDErepr", self.prefix_repr, self.suffix_repr)


class AddStringToExcFromCodeTest(AddStringToExcTest):
    """Generic class for tests about add_string_to_exception.

    The tested function is called on an exception created by running
    some failing code (`self.code`) and catching what it throws.
    """

    code = NotImplemented

    def get_exception(self):
        """Get the exception by running the code and catching errors."""
        type_, value, _ = common.get_exception(self.code)
        self.assertTrue(
            issubclass(type_, self.error_type),
            "{0} ({1}) not a subclass of {2}"
            .format(type_, value, self.error_type))
        return value


class AddStringToNameErrorTest(unittest2.TestCase, AddStringToExcFromCodeTest):
    """Class for tests of add_string_to_exception on NameError."""

    code = 'babar = 0\nbaba'
    error_type = NameError


class AddStringToTypeErrorTest(unittest2.TestCase, AddStringToExcFromCodeTest):
    """Class for tests of add_string_to_exception on TypeError."""

    code = '[0](0)'
    error_type = TypeError


class AddStringToImportErrorTest(
        unittest2.TestCase, AddStringToExcFromCodeTest):
    """Class for tests of add_string_to_exception on ImportError."""

    code = 'import maths'
    error_type = ImportError


class AddStringToKeyErrorTest(
        unittest2.TestCase, AddStringToExcFromCodeTest):
    """Class for tests of add_string_to_exception on KeyError."""

    code = 'dict()["ffdsqmjklfqsd"]'
    error_type = KeyError


class AddStringToAttributeErrorTest(
        unittest2.TestCase, AddStringToExcFromCodeTest):
    """Class for tests of add_string_to_exception on AttributeError."""

    code = '[].does_not_exist'
    error_type = AttributeError


class AddStringToSyntaxErrorTest(
        unittest2.TestCase, AddStringToExcFromCodeTest):
    """Class for tests of add_string_to_exception on SyntaxError."""

    code = 'return'
    error_type = SyntaxError


class AddStringToMemoryErrorTest(
        unittest2.TestCase, AddStringToExcFromCodeTest):
    """Class for tests of add_string_to_exception on MemoryError."""

    code = '[0] * 999999999999999'
    error_type = MemoryError
    prefix_repr = "'"
    suffix_repr = "',"


class AddStringToIOErrorTest(
        unittest2.TestCase, AddStringToExcFromCodeTest):
    """Class for tests of add_string_to_exception on NoFileIoError."""

    code = 'with open("/does_not_exist") as f:\n\tpass'
    error_type = common.NoFileIoError


class AddStringToUnicodeDecodeTest(
        unittest2.TestCase, AddStringToExcFromCodeTest):
    """Class for tests of add_string_to_exception on UnicodeDecodeError."""

    code = "'foo'.encode('utf-16').decode('utf-8')"
    error_type = UnicodeDecodeError


class AddStringToUnicodeEncodeTest(
        unittest2.TestCase, AddStringToExcFromCodeTest):
    """Class for tests of add_string_to_exception on UnicodeEncodeError."""

    code = U_PREFIX + '"\u0411".encode("iso-8859-15")'
    error_type = UnicodeEncodeError


class AddStringToExcFromInstanceTest(AddStringToExcTest):
    """Generic class for tests about add_string_to_exception.

    The tested function is called on an exception created by calling the
    constructor (`self.exc_type`) with the right arguments (`self.args`).
    Because of the way it creates exception, the tests are somewhat artificial
    (compared to AddStringToExcFromCodeTest for instance). However, the major
    advantage is that they can be easily generated (to have all subclasses of
    Exception tested).
    """

    check_str_sum = False
    exc_type = NotImplemented
    args = NotImplemented

    def get_exception(self):
        """Get the exception by calling the constructor with correct args."""
        return self.exc_type(*self.args)


class AddStringToZeroDivisionError(
        unittest2.TestCase, AddStringToExcFromInstanceTest):
    """Class for tests of add_string_to_exception on ZeroDivisionError."""

    exc_type = ZeroDivisionError
    args = ('', '', '', '', '')


def get_instance(klass):
    """Get instance for class by bruteforcing the parameters.

    Construction is attempted with a decreasing number of arguments so that
    the instanciated object has as many non-null attributes set as possible.
    This is important not for the creation but when the object gets used
    later on. Also, the order of the values has its importance for similar
    reasons.
    """
    my_unicode = str if sys.version_info >= (3, 0) else unicode
    values_tried = [my_unicode(), bytes(), 0]
    for nb_arg in reversed(range(6)):
        for p in itertools.product(values_tried, repeat=nb_arg):
            try:
                return klass(*p), p
            except (TypeError, AttributeError) as e:
                pass
            except Exception as e:
                print(type(e), e)
    return None


def generate_add_string_to_exc_tests():
    """Generate tests for add_string_to_exception.

    This function dynamically creates tests cases for the function
    add_string_to_exception for as many Exception subclasses as possible.
    This is not used at the moment because the generated classes need to
    be added in the global namespace and there is no good way to do this.
    However, it may be a good idea to call this when new versions of
    Python are released to ensure we handle all exceptions properly (and
    find the tests to be added manually if need be).
    """
    for klass in get_subclasses(Exception):
        r = get_instance(klass)
        if r is not None:
            _, p = r
            class_name = ("NameForAddStringToExcFromInstanceTest" +
                          klass.__name__ + str(id(klass)))
            assert class_name not in globals(), class_name
            globals()[class_name] = type(
                    class_name,
                    (AddStringToExcFromInstanceTest, unittest2.TestCase),
                    {'exc_type': klass, 'args': p})


if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
