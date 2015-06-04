# -*- coding: utf-8
"""Common logic for unit tests."""
import sys


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


class CommonTestOldStyleClass:
    """ Dummy class for testing purposes."""
    pass


class CommonTestOldStyleClass2:
    """ Dummy class for testing purposes."""
    pass


class CommonTestNewStyleClass(object):
    """ Dummy class for testing purposes."""
    pass


class CommonTestNewStyleClass2(object):
    """ Dummy class for testing purposes."""
    pass


class TestWithStringFunction(object):
    """ Unit test class with an helper method. """

    def assertStringAdded(self, string, before, after, concat=True, adj=0):
        """ Check that `string` has been added to `before` to get `after`.
        In some representation, string is not added via pure concatenation but
        can be added anywhere. Reusing as many already defined assert methods
        to have the pretty printing.
        - Argument `concat` is used to know whether concatenation is to be
        checked (after = before + string)
        `adj` is used as an adjustment when comparing string lengths."""
        if string:
            self.assertNotEqual(before, after)
            self.assertFalse(string in before, before)
            self.assertTrue(string in after, after)
            self.assertEqual(len(after), len(before) + len(string) + adj)
            if concat:
                self.assertEqual(before + string, after)
        else:
            self.assertEqual(before, after)

if __name__ == '__main__':
    print(sys.version_info)
