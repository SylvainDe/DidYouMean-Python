# -*- coding: utf-8
"""Unit tests for code in didyoumean_internal.py."""
from didyoumean_internal import get_suggestion_string, add_string_to_exception,\
    get_objects_in_frame, get_subclasses, get_types_for_str,\
    get_types_for_str_using_inheritance,\
    get_types_for_str_using_names
import didyoumean_common_tests as common
from didyoumean_common_tests import CommonTestOldStyleClass2,\
    CommonTestNewStyleClass2  # to have these 2 in defined names
import unittest2
import sys


OLD_CLASS_SUPPORT = sys.version_info >= (3, 0)
IS_PYPY = hasattr(sys, "pypy_translation_info")
global_var = 42  # Please don't change the value


class GetObjectInFrameTests(unittest2.TestCase):
    """ Class for tests related to frame/backtrace/etc inspection.

    Tested functions are : get_objects_in_frame."""

    def name_corresponds_to(self, name, expected):
        """ Helper functions to test get_objects_in_frame.

        Check that the name corresponds to the expected objects (and their
        scope) in the frame of calling function.
        None can be used to match any object as it can be hard to describe
        an object when it is hidden by something in a closer scope.
        Also, extra care is to be taken when calling the function because
        giving value by names might affect the result (adding in local
        scope.)"""
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
        """ Test with builtin. """
        builtin = len
        name = builtin.__name__
        self.name_corresponds_to(name, [(builtin, 'builtin')])

    def test_builtin2(self):
        """ Test with builtin. """
        name = 'True'
        self.name_corresponds_to(name, [(bool(1), 'builtin')])

    def test_global(self):
        """ Test with global. """
        name = 'global_var'
        self.name_corresponds_to(name, [(42, 'global')])

    def test_local(self):
        """ Test with local. """
        name = 'toto'
        self.name_corresponds_to(name, [])
        toto = 0
        self.name_corresponds_to(name, [(0, 'local')])

    def test_local_and_global(self):
        """ Test with local hiding a global. """
        name = 'global_var'
        self.name_corresponds_to(name, [(42, 'global')])
        global_var = 1
        self.name_corresponds_to(name, [(1, 'local'), (42, 'global')])

    def test_global_keword(self):
        """ Test with global keyword. """
        name = 'global_var'
        global_var = 42  # value is unchanged
        self.name_corresponds_to(name, [(42, 'global')])
        global global_var  # has an effect even at the end

    def test_del_local(self):
        """ Test with deleted local. """
        name = 'toto'
        self.name_corresponds_to(name, [])
        toto = 0
        self.name_corresponds_to(name, [(0, 'local')])
        del toto
        self.name_corresponds_to(name, [])

    def test_del_local_hiding_global(self):
        """ Test with deleted local hiding a global. """
        name = 'global_var'
        glob_desc = [(42, 'global')]
        local_desc = [(1, 'local')]
        self.name_corresponds_to(name, glob_desc)
        global_var = 1
        self.name_corresponds_to(name, local_desc + glob_desc)
        del global_var
        self.name_corresponds_to(name, glob_desc)

    def test_enclosing(self):
        """ Test with nested functions. """
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
        """ Test with nested functions. """
        bar = 2

        def nested_func():
            self.name_corresponds_to('bar', [])
            bar = 3
            self.name_corresponds_to('bar', [(3, 'local')])

        nested_func()
        self.name_corresponds_to('nested_func', [(nested_func, 'local')])

    def test_enclosing3(self):
        """ Test with nested functions. """
        bar = 2

        def nested_func():
            self.name_corresponds_to('bar', [(2, 'local')])
            tmp = bar
            self.name_corresponds_to('bar', [(2, 'local')])

        nested_func()
        self.name_corresponds_to('nested_func', [(nested_func, 'local')])

    def test_enclosing4(self):
        """ Test with nested functions. """
        global_var = 1

        def nested_func():
            self.name_corresponds_to('global_var', [(42, 'global')])

        nested_func()
        self.name_corresponds_to('global_var', [(1, 'local'), (42, 'global')])

    def test_enclosing5(self):
        """ Test with nested functions. """
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
    """ Dummy class for testing purposes."""
    pass


class OldStyleDerivedClass(OldStyleBaseClass):
    """ Dummy class for testing purposes."""
    pass


class NewStyleBaseClass(object):
    """ Dummy class for testing purposes."""
    pass


class NewStyleDerivedClass(NewStyleBaseClass):
    """ Dummy class for testing purposes."""
    pass


def a_function():
    """ Dummy function for testing purposes."""
    pass


def a_generator():
    """ Dummy generator for testing purposes."""
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
    """Tests about get_types_for_str."""

    def test_get_subclasses(self):
        """Tests for the get_subclasses function.

        All types are found when looking for subclasses of object, except
        for the old style classes on Python 2.x."""
        all_classes = get_subclasses(object)
        for typ, new in CLASSES:
            self.assertTrue(typ in get_subclasses(typ))
            if new or OLD_CLASS_SUPPORT:
                self.assertTrue(typ in all_classes)
            else:
                self.assertFalse(typ in all_classes)
        self.assertFalse(0 in all_classes)

    def test_get_types_for_str_using_inheritance(self):
        """Tests for the get_types_for_str_using_inheritance function.

        All types are found when looking for subclasses of object, except
        for the old style classes on Python 2.x.

        Also, it seems like the returns is (almost) always precise as the
        returned set contains only the expected type and nothing else."""
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
        """Tests for the get_types_using_names function.

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
        """Tests for the get_types_for_str.

        Checks that for all tested types, the proper type is retrieved."""
        for typ, _ in CLASSES:
            types = self.get_types_for_str(typ.__name__)
            self.assertEqual(types, set([typ]), typ)

        self.assertEqual(self.get_types_for_str('faketype'), set())

    def test_get_types_for_str2(self):
        """Tests for the get_types_for_str.

        Checks that for all tested strings, a single type is retrived.
        This is useful to ensure that we are using the right names."""
        for n in ['module', 'NoneType', 'function',
                  'NewStyleBaseClass', 'NewStyleDerivedClass',
                  'OldStyleBaseClass', 'OldStyleDerivedClass']:
            types = self.get_types_for_str(n)
            self.assertEqual(len(types), 1, n)
        for n in ['generator']:  # FIXME: with pypy, we find an additional type
            types = self.get_types_for_str(n)
            self.assertEqual(len(types), 2 if IS_PYPY else 1, n)

    def test_old_class_not_in_namespace(self):
        # FIXME: At the moment, CommonTestOldStyleClass is not found
        # because it is not in the namespace.
        typ = common.CommonTestOldStyleClass
        expect_with_inherit = set([typ]) if OLD_CLASS_SUPPORT else set()
        name = typ.__name__
        types1 = get_types_for_str_using_inheritance(name)
        types2 = self.get_types_using_names(name)
        types3 = self.get_types_for_str(name)
        self.assertEqual(types1, expect_with_inherit)
        self.assertEqual(types2, set())
        self.assertEqual(types3, expect_with_inherit)


class GetSuggStringTests(unittest2.TestCase):
    """ Tests about get_suggestion_string. """

    def test_no_sugg(self):
        """ Empty list of suggestions. """
        self.assertEqual(get_suggestion_string(()), "")

    def test_one_sugg(self):
        """ Single suggestion. """
        self.assertEqual(get_suggestion_string(('0',)), ". Did you mean 0?")

    def test_same_sugg(self):
        """ Identical suggestion. """
        self.assertEqual(
            get_suggestion_string(('0', '0')), ". Did you mean 0, 0?")

    def test_multiple_suggs(self):
        """ Multiple suggestions. """
        self.assertEqual(
            get_suggestion_string(('0', '1')), ". Did you mean 0, 1?")


class AddStringToExcTest(
        unittest2.TestCase, common.TestWithStringFunction):
    """ Tests about add_string_to_exception. """

    def get_exc_as_str_before_and_after(self, code, type_arg, string):
        """ Retrieve string representations of exceptions raised by code
        before and after calling add_string_to_exception. """
        type_, value, _ = common.get_exception(code)
        self.assertEqual(type_arg, type_)
        str1, repr1 = str(value), repr(value)
        add_string_to_exception(value, string)
        str2, repr2 = str(value), repr(value)
        return (str1, repr1, str2, repr2)

    def test_add_empty_string(self):
        """ Empty string added to NameError. """
        string = ""
        code = 'babar = 0\nbaba'
        str1, repr1, str2, repr2 = self.get_exc_as_str_before_and_after(
            code, NameError, string)
        self.assertStringAdded(string, str1, str2)
        self.assertStringAdded(string, repr1, repr2)

    def test_add_string(self):
        """ Non-empty string added to NameError. """
        string = "ABCDEF"
        code = 'babar = 0\nbaba'
        str1, repr1, str2, repr2 = self.get_exc_as_str_before_and_after(
            code, NameError, string)
        self.assertStringAdded(string, str1, str2)
        self.assertStringAdded(string, repr1, repr2, False)

    def test_add_empty_string_to_syntaxerr(self):
        """ Empty string added to SyntaxError. """
        string = ""
        code = 'return'
        str1, repr1, str2, repr2 = self.get_exc_as_str_before_and_after(
            code, SyntaxError, string)
        self.assertStringAdded(string, str1, str2)
        self.assertStringAdded(string, repr1, repr2)

    def test_add_string_to_syntaxerr(self):
        """ Non-empty string added to SyntaxError. """
        string = "ABCDEF"
        code = 'return'
        str1, repr1, str2, repr2 = self.get_exc_as_str_before_and_after(
            code, SyntaxError, string)
        self.assertStringAdded(string, str1, str2, False)
        self.assertStringAdded(string, repr1, repr2, False)

    def test_add_empty_string_to_memoryerr(self):
        """ Empty string added to MemoryError. """
        string = ""
        code = '[0] * 999999999999999'
        str1, repr1, str2, repr2 = self.get_exc_as_str_before_and_after(
            code, MemoryError, string)
        self.assertStringAdded(string, str1, str2)
        self.assertStringAdded(string, repr1, repr2)

    def test_add_string_to_memoryerr(self):
        """ Non-empty string added to MemoryError. """
        string = "ABCDEF"
        code = '[0] * 999999999999999'
        str1, repr1, str2, repr2 = self.get_exc_as_str_before_and_after(
            code, MemoryError, string)
        self.assertStringAdded(string, str1, str2)
        self.assertStringAdded(string, repr1, repr2, False, 3)


if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
