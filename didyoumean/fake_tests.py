# -*- coding: utf-8
"""Fake unit tests."""
try:
    import unittest2
    unittest_module = unittest2
except ImportError:
    import unittest
    unittest_module = unittest
except AttributeError:
    import unittest
    unittest_module = unittest


class Testing(unittest_module.TestCase):
    def test_string(self):
        a = 'some'
        b = 'some'
        self.assertEqual(a, b)

