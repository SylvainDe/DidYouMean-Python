# -*- coding: utf-8
"""Unit tests for regexps from didyoumean_re.py."""
import unittest2
import didyoumean_re as re
import sys

NO_GROUP = ((), dict())


class RegexTests(unittest2.TestCase):
    """Tests to check that error messages match the regexps."""

    def re_matches(self, text, regexp, results):
        """Check that text matches regexp and gives the right match groups.

        result is a tuple containing the expected return values for groups()
        and groupdict().
        """
        groups, named_groups = results
        self.assertRegexpMatches(text, regexp)   # does pretty printing
        match = re.match(regexp, text)
        self.assertTrue(match)
        self.assertEqual(groups, match.groups())
        self.assertEqual(named_groups, match.groupdict())

    def test_unbound_assignment(self):
        """Test VARREFBEFOREASSIGN_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
            "local variable 'some_var' referenced before assignment",
            "free variable 'some_var' referenced before assignment " \
            "in enclosing scope",
        ]
        groups = ('some_var',)
        named_groups = {'name': 'some_var'}
        results = (groups, named_groups)
        for msg in msgs:
            self.re_matches(msg, re.VARREFBEFOREASSIGN_RE, results)

    def test_name_not_defined(self):
        """Test NAMENOTDEFINED_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy3
            "name 'some_name' is not defined",
            # Python 2.6/2.7/3.2/3.3/PyPy/PyPy3
            "global name 'some_name' is not defined",
        ]
        groups = ('some_name',)
        named_groups = {'name': 'some_name'}
        for msg in msgs:
            self.re_matches(msg, re.NAMENOTDEFINED_RE, (groups, named_groups))

    def test_attribute_error(self):
        """Test ATTRIBUTEERROR_RE."""
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
        }
        for group, msgs in group_msg.items():
            for msg in msgs:
                self.re_matches(msg, re.ATTRIBUTEERROR_RE, (group, dict()))

    def test_module_attribute_error(self):
        """Test MODULEHASNOATTRIBUTE_RE."""
        # Python 3.5
        msg = "module 'some_module' has no attribute 'attri'"
        group = ('some_module', 'attri')
        self.re_matches(msg, re.MODULEHASNOATTRIBUTE_RE, (group, dict()))

    def test_cannot_import(self):
        """Test CANNOTIMPORT_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3
            "cannot import name pie",
            # Python 3.4/3.5/PyPy/PyPy3
            "cannot import name 'pie'",
        ]
        groups = ('pie',)
        for msg in msgs:
            self.re_matches(msg, re.CANNOTIMPORT_RE, (groups, dict()))

    def test_no_module_named(self):
        """Test NOMODULE_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/PyPy/PyPy3
            "No module named fake_module",
            # Python 3.3/3.4/3.5
            "No module named 'fake_module'",
        ]
        groups = ('fake_module',)
        for msg in msgs:
            self.re_matches(msg, re.NOMODULE_RE, (groups, dict()))

    def test_index_out_of_range(self):
        """Test INDEXOUTOFRANGE_RE."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "list index out of range"
        self.re_matches(msg, re.INDEXOUTOFRANGE_RE, NO_GROUP)

    def test_unsubscriptable(self):
        """Test UNSUBSCRIBTABLE_RE."""
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
            self.re_matches(msg, re.UNSUBSCRIBTABLE_RE, (groups, dict()))

    def test_unexpected_kw_arg(self):
        """Test UNEXPECTED_KEYWORDARG_RE."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "some_func() got an unexpected keyword argument 'a'"
        groups = ('some_func', 'a')
        self.re_matches(msg, re.UNEXPECTED_KEYWORDARG_RE, (groups, dict()))

    def test_unexpected_kw_arg2(self):
        """Test UNEXPECTED_KEYWORDARG2_RE."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5
        msg = "'this_doesnt_exist' is an invalid " \
            "keyword argument for this function"
        groups = ('this_doesnt_exist', )
        self.re_matches(msg, re.UNEXPECTED_KEYWORDARG2_RE, (groups, dict()))

    def test_unexpected_kw_arg3(self):
        """Test UNEXPECTED_KEYWORDARG3_RE."""
        # PyPy/PyPy3
        msg = "invalid keyword arguments to print()"
        groups = ('print', )
        self.re_matches(msg, re.UNEXPECTED_KEYWORDARG3_RE, (groups, dict()))

    def test_zero_length_field(self):
        """Test ZERO_LEN_FIELD_RE."""
        # Python 2.6
        msg = "zero length field name in format"
        self.re_matches(msg, re.ZERO_LEN_FIELD_RE, NO_GROUP)

    def test_math_domain_error(self):
        """Test MATH_DOMAIN_ERROR_RE."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "math domain error"
        self.re_matches(msg, re.MATH_DOMAIN_ERROR_RE, NO_GROUP)

    def test_too_many_values(self):
        """Test TOO_MANY_VALUES_UNPACK_RE."""
        msgs = [
            # Python 2.6/2.7
            "too many values to unpack",
            # Python 3.2/3.3/3.4/3.5/PyPy3
            "too many values to unpack (expected 3)",
        ]
        for msg in msgs:
            self.re_matches(msg, re.TOO_MANY_VALUES_UNPACK_RE, NO_GROUP)

    def test_unhashable_type(self):
        """Test UNHASHABLE_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5
            "unhashable type: 'list'",
            # PyPy/PyPy3
            "'list' objects are unhashable",
        ]
        groups = ('list',)
        for msg in msgs:
            self.re_matches(msg, re.UNHASHABLE_RE, (groups, dict()))

    def test_outside_function(self):
        """Test OUTSIDE_FUNCTION_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
            "'return' outside function",
            # PyPy/PyPy3
            "return outside function",
        ]
        groups = ('return',)
        for msg in msgs:
            self.re_matches(msg, re.OUTSIDE_FUNCTION_RE, (groups, dict()))

    def test_nb_positional_argument(self):
        """Test NB_ARG_RE."""
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
            self.re_matches(msg, re.NB_ARG_RE, (groups, dict()))

    def test_missing_positional_arg(self):
        """Test MISSING_POS_ARG_RE."""
        msgs = [
            # Python 3.3/3.4/3.5
            "some_func() missing 2 required positional arguments: "
            "'much' and 'args'",
            "some_func() missing 1 required positional argument: "
            "'much'",
        ]
        groups = ('some_func',)
        for msg in msgs:
            self.re_matches(msg, re.MISSING_POS_ARG_RE, (groups, dict()))

    def test_need_more_values_to_unpack(self):
        """Test NEED_MORE_VALUES_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5(?)/PyPy3
            "need more than 2 values to unpack",
            # Python 3.5
            "not enough values to unpack (expected 3, got 2)",
        ]
        for msg in msgs:
            self.re_matches(msg, re.NEED_MORE_VALUES_RE, NO_GROUP)

    def test_missing_parentheses(self):
        """Test MISSING_PARENT_RE."""
        # Python 3.4/3.5
        msg = "Missing parentheses in call to 'exec'"
        groups = ('exec',)
        self.re_matches(msg, re.MISSING_PARENT_RE, (groups, dict()))

    def test_invalid_literal(self):
        """Test INVALID_LITERAL_RE."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "invalid literal for int() with base 10: 'toto'"
        groups = ('int', 'toto')
        self.re_matches(msg, re.INVALID_LITERAL_RE, (groups, dict()))

    def test_invalid_syntax(self):
        """Test INVALID_SYNTAX_RE."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy3
        msg = "invalid syntax"
        self.re_matches(msg, re.INVALID_SYNTAX_RE, NO_GROUP)

    def test_invalid_comp(self):
        """Test INVALID_COMP_RE."""
        # PyPy3
        msg = "invalid comparison"
        self.re_matches(msg, re.INVALID_COMP_RE, NO_GROUP)

    def test_expected_length(self):
        """Test EXPECTED_LENGTH_RE."""
        # PyPy
        msg = "expected length 3, got 2"
        groups = ('3', '2')
        self.re_matches(msg, re.EXPECTED_LENGTH_RE, (groups, dict()))

    def test_future_first(self):
        """Test FUTURE_FIRST_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5
            "from __future__ imports must occur at the beginning of the file",
            # PyPy/PyPy3
            "__future__ statements must appear at beginning of file",
        ]
        for msg in msgs:
            self.re_matches(msg, re.FUTURE_FIRST_RE, NO_GROUP)

    def test_future_feature_not_def(self):
        """Test FUTURE_FEATURE_NOT_DEF_RE."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "future feature divisio is not defined"
        groups = ('divisio',)
        self.re_matches(msg, re.FUTURE_FEATURE_NOT_DEF_RE, (groups, dict()))

    def test_result_has_too_many_items(self):
        """Test RESULT_TOO_MANY_ITEMS_RE."""
        # Python 2.6
        msg = "range() result has too many items"
        groups = ('range',)
        self.re_matches(msg, re.RESULT_TOO_MANY_ITEMS_RE, (groups, dict()))

    def test_unqualified_exec(self):
        """Test UNQUALIFIED_EXEC_RE."""
        msgs = [
            # Python 2.6
            "unqualified exec is not allowed in function 'func_name' "
            "it is a nested function",
            # Python 2.7
            "unqualified exec is not allowed in function 'func_name' "
            "because it is a nested function",
            # Python 2.6
            "unqualified exec is not allowed in function 'func_name' "
            "it contains a nested function with free variables",
            # Python 2.7
            "unqualified exec is not allowed in function 'func_name' "
            "because it contains a nested function with free variables",
        ]
        for msg in msgs:
            self.re_matches(msg, re.UNQUALIFIED_EXEC_RE, NO_GROUP)

    def test_import_star(self):
        """Test IMPORTSTAR_RE."""
        msgs = [
            # Python 2.6
            "import * is not allowed in function 'func_name' because it "
            "is contains a nested function with free variables",
            # Python 2.7
            "import * is not allowed in function 'func_name' because it "
            "contains a nested function with free variables",
            # Python 2.6
            "import * is not allowed in function 'func_name' because it "
            "is is a nested function",
            # Python 2.7
            "import * is not allowed in function 'func_name' because it "
            "is a nested function",
            # Python 3
            "import * only allowed at module level"
        ]
        for msg in msgs:
            self.re_matches(msg, re.IMPORTSTAR_RE, NO_GROUP)

    def test_does_not_support(self):
        """Test OBJ_DOES_NOT_SUPPORT_RE."""
        msg = "'range' object does not support item assignment"
        groups = ('range',)
        self.re_matches(msg, re.OBJ_DOES_NOT_SUPPORT_RE, (groups, dict()))

    def test_cant_convert(self):
        """Test CANT_CONVERT_RE."""
        msg = "Can't convert 'int' object to str implicitly"
        groups = ('int', 'str')
        self.re_matches(msg, re.CANT_CONVERT_RE, (groups, dict()))

    def test_cannot_concat(self):
        """Test CANNOT_CONCAT_RE."""
        msg = "cannot concatenate 'str' and 'int' objects"
        groups = ('str', 'int')
        self.re_matches(msg, re.CANNOT_CONCAT_RE, (groups, dict()))

    def test_unsupported_operand(self):
        """Test UNSUPPORTED_OP_RE."""
        msg = "unsupported operand type(s) for +: 'int' and 'str'"
        groups = ('+', 'int', 'str')
        self.re_matches(msg, re.UNSUPPORTED_OP_RE, (groups, dict()))

    def test_not_callable(self):
        """Test NOT_CALLABLE_RE."""
        msg = "'list' object is not callable"
        groups = ('list',)
        self.re_matches(msg, re.NOT_CALLABLE_RE, (groups, dict()))

    def test_descriptor_requires(self):
        """Test DESCRIPT_REQUIRES_TYPE_RE."""
        msg = "descriptor 'add' requires a 'set' object but received a 'int'"
        groups = ('add', 'set', 'int')
        self.re_matches(
            msg, re.DESCRIPT_REQUIRES_TYPE_RE, (groups, dict()))

    def test_argument_not_iterable(self):
        """Test ARG_NOT_ITERABLE_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5
            "argument of type 'type' is not iterable",
            # PyPy/PyPy3
            "'type' object is not iterable"
        ]
        groups = ('type',)
        for msg in msgs:
            self.re_matches(msg, re.ARG_NOT_ITERABLE_RE, (groups, dict()))

    def test_must_be_called_with_instance(self):
        """Test MUST_BE_CALLED_WITH_INST_RE."""
        msg = "unbound method add() must be called with set " \
              "instance as first argument (got int instance instead)"
        groups = ('add', 'set', 'int')
        self.re_matches(
            msg, re.MUST_BE_CALLED_WITH_INST_RE, (groups, dict()))

    def test_object_has_no(self):
        """Test OBJECT_HAS_NO_FUNC_RE."""
        msgs = {
            # Python 2.6/2.7/3.2/3.3/3.4/3.5
            'len': "object of type 'generator' has no len()",
            # PyPy/PyPy3
            'length': "'generator' has no length",
        }
        for name, msg in msgs.items():
            groups = ('generator', name)
            self.re_matches(msg, re.OBJECT_HAS_NO_FUNC_RE, (groups, dict()))

    def test_nobinding_nonlocal(self):
        """Test NO_BINDING_NONLOCAL_RE."""
        msg = "no binding for nonlocal 'foo' found"
        groups = ('foo',)
        self.re_matches(msg, re.NO_BINDING_NONLOCAL_RE, (groups, dict()))

    def test_nosuchfile(self):
        """Test NO_SUCH_FILE_RE."""
        msg = "No such file or directory"
        self.re_matches(msg, re.NO_SUCH_FILE_RE, NO_GROUP)


if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
