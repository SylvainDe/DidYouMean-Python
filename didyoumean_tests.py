# -*- coding: utf-8
"""Unit tests for code in didyoumean.py."""
from didyoumean import didyoumean
import unittest


class NameErrorSingleArgument(unittest.TestCase):
    def nameerror_function(self, foo, bar):
        return foob

    @didyoumean
    def nameerror_function_wrapped(self, foo, bar):
        return self.nameerror_function(foo, bar)

    def test_original(self):
        self.assertRaisesRegex(NameError, "^(global )?name '[^']*' is not defined$", lambda: self.nameerror_function(1, 2))

    def test_wrapped(self):
        self.assertRaisesRegex(NameError, "^(global )?name '[^']*' is not defined. Did you mean foo$", lambda: self.nameerror_function_wrapped(1, 2))


class NameErrorMultipleArguments(unittest.TestCase):
    def nameerror_function(self, fool, foot):
        return food

    @didyoumean
    def nameerror_function_wrapped(self, foo, bar):
        return self.nameerror_function(foo, bar)

    def test_original(self):
        self.assertRaisesRegex(NameError, "^(global )?name '[^']*' is not defined$", lambda: self.nameerror_function(1, 2))

    def test_wrapped(self):
        self.assertRaisesRegex(NameError, "^(global )?name '[^']*' is not defined. Did you mean foot, fool$", lambda: self.nameerror_function_wrapped(1, 2))


class NameErrorBuiltin(unittest.TestCase):
    def nameerror_function(self):
        return maxi

    @didyoumean
    def nameerror_function_wrapped(self):
        return self.nameerror_function()

    def test_original(self):
        self.assertRaisesRegex(NameError, "^(global )?name '[^']*' is not defined$", lambda: self.nameerror_function())

    def test_wrapped(self):
        self.assertRaisesRegex(NameError, "^(global )?name '[^']*' is not defined. Did you mean max$", lambda: self.nameerror_function_wrapped())


class NameErrorNoSuggestion(unittest.TestCase):
    def nameerror_function(self):
        return ldkjhfnvdlkjhvgfdhgf

    @didyoumean
    def nameerror_function_wrapped(self):
        return self.nameerror_function()

    def test_original(self):
        self.assertRaisesRegex(NameError, "^(global )?name '[^']*' is not defined$", lambda: self.nameerror_function())

    def test_wrapped(self):
        self.assertRaisesRegex(NameError, "^(global )?name '[^']*' is not defined$", lambda: self.nameerror_function_wrapped())


class AttributeErrorBuiltin(unittest.TestCase):
    def attributeerror_function(self):
        lst = [1, 2, 3]
        lst.len()

    @didyoumean
    def attributeerror_function_wrapped(self):
        return self.attributeerror_function()

    def test_original(self):
        self.assertRaisesRegex(AttributeError, "^'[^']*' object has no attribute '[^']*'$", lambda: self.attributeerror_function())

    def test_wrapped(self):
        self.assertRaisesRegex(AttributeError, "^'[^']*' object has no attribute '[^']*'. Did you mean len\(list\)$", lambda: self.attributeerror_function_wrapped())


class AttributeErrorMethod(unittest.TestCase):
    def attributeerror_function(self):
        lst = [1, 2, 3]
        lst.appendh(4)

    @didyoumean
    def attributeerror_function_wrapped(self):
        return self.attributeerror_function()

    def test_original(self):
        self.assertRaisesRegex(AttributeError, "^'[^']*' object has no attribute '[^']*'$", lambda: self.attributeerror_function())

    def test_wrapped(self):
        self.assertRaisesRegex(AttributeError, "^'[^']*' object has no attribute '[^']*'. Did you mean append*$", lambda: self.attributeerror_function_wrapped())
