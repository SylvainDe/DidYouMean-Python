# -*- coding: utf-8
"""Common logic for unit tests."""
import sys

try:
    import unittest2
    unittest_module = unittest2
except ImportError:
    import unittest
    unittest_module = unittest

# Tests based on MemoryError may required some tweaking to run depending
# on both the hardware and the software used. This flag can be used to
# disable the corresponding tests easily.
SKIP_MEMORY_ERROR_TESTS = False

old_errors = (IOError, OSError)

try:
    NoFileIoError = NoFileOsError = FileNotFoundError
except NameError:
    NoFileIoError, NoFileOsError = old_errors

try:
    IsDirIoError = IsDirOsError = IsADirectoryError
except NameError:
    IsDirIoError, IsDirOsError = old_errors


try:
    NotDirIoError = NotDirOsError = NotADirectoryError
except NameError:
    NotDirIoError, NotDirOsError = old_errors


def no_exception(code):
    """Helper function to run code and check it works."""
    exec(code)


def get_exception(code):
    """Helper function to run code and get what it throws."""
    try:
        no_exception(code)
    except:
        return sys.exc_info()
    return None


class CommonTestOldStyleClass:
    """Dummy class for testing purposes."""

    pass


class CommonTestOldStyleClass2:
    """Dummy class for testing purposes."""

    pass


class CommonTestNewStyleClass(object):
    """Dummy class for testing purposes."""

    pass


class CommonTestNewStyleClass2(object):
    """Dummy class for testing purposes."""

    pass


class TestWithStringFunction(object):
    """Unit test class with an helper method."""

    def assertIn(self, first, second):
        """Check that `first` argument is in `second`.

        Just like self.assertTrue(a in b), but with a nicer default message.
        This is part of standard library but only from Python 2.7.
        """
        msg = '"%s" not found in "%s"' % (first, second)
        self.assertTrue(first in second, msg)

    def assertNotIn(self, first, second):
        """Check that `first` argument is NOT in `second`.

        Just like self.assertFalse(a in b), but with a nicer default message.
        This is part of standard library but only from Python 2.7.
        """
        msg = '"%s" unexpectedly found in "%s"' % (first, second)
        self.assertFalse(first in second, msg)

    def assertStringAdded(self, string, before, after, check_str_sum):
        """Check that `string` has been added to `before` to get `after`.

        If the `check_str_sum` argument is True, we check that adding `string`
        somewhere in the `before` string gives the `after` string. If the
        argument is false, we just check that `string` can be found in `after`
        but not in `before`.
        """
        if string:
            self.assertNotEqual(before, after)
            self.assertNotIn(string, before)
            self.assertIn(string, after)
            # Removing string and checking that we get the original string
            begin, mid, end = after.partition(string)
            self.assertEqual(mid, string)
            if check_str_sum:
                self.assertEqual(begin + end, before)
        else:
            self.assertEqual(before, after)

if __name__ == '__main__':
    print(sys.version_info)
