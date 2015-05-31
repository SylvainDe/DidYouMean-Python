# -*- coding: utf-8
"""Unit tests for code in didyoumean.py."""
from didyoumean import get_suggestion_string, add_string_to_exception,\
    get_objects_in_frame
from didyoumean_common_tests import TestWithStringFunction,\
    get_exception
import unittest2
import sys


global_var = 42  # Please don't change the value


class InspectionTests(unittest2.TestCase):
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
            self.assertEqual(scope, expscope)
            if expobj is not None:
                self.assertEqual(obj, expobj)

    def test_builtin(self):
        """ Test with builtin. """
        builtin = len
        name = builtin.__name__
        self.name_corresponds_to(name, [(builtin, 'builtin')])

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


class AddStringToExcTest(unittest2.TestCase, TestWithStringFunction):
    """ Tests about add_string_to_exception. """

    def get_exc_as_str_before_and_after(self, code, type_arg, string):
        """ Retrieve string representations of exceptions raised by code
        before and after calling add_string_to_exception. """
        type_, value, _ = get_exception(code)
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
