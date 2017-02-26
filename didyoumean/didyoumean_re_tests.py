# -*- coding: utf-8
"""Unit tests for regexps from didyoumean_re.py."""
import unittest2
import didyoumean_re as re
import sys
from didyoumean_internal import get_subclasses

NO_GROUP = ((), dict())
# Various technical flags to check more that meet the eyes in tests
# Flag used to check that a text only match the expected regexp and not
# the other to ensure we do not have ambiguous/double regexp matching.
CHECK_OTHERS_DONT_MATCH = True
# Flag to check that the regexp provided does correspond to a regexp
# listed in re.ALL_REGEXPS
CHECK_RE_LISTED = True
# Flag to check that the name used for the regexp in re.ALL_REGEXPS
# does match the naming convention
CHECK_RE_NAME = True
# Flag to check that the regex does match a few conventions such as:
# stars with ^, ends with $.
CHECK_RE_VALUE = True


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
        self.check_more_about_re(text, regexp)

    def check_more_about_re(self, text, regexp):
        """Check various properties about the regexp.

        Properties checked are configurable via global constants. These
        properties are not stricly speaking required but they help to
        detect potential issues much more quickly.
        """
        if CHECK_RE_VALUE:
            self.assertTrue(regexp.startswith('^'))
            self.assertTrue(regexp.endswith('$'))
        found = False
        for other_name, other_re in re.ALL_REGEXPS.items():
            if other_re == regexp:
                found = True
                if CHECK_RE_NAME:
                    self.assertTrue(other_name.endswith('_RE'))
            elif CHECK_OTHERS_DONT_MATCH:
                details = "text '%s' matches %s (on top of %s)" % \
                        (text, other_name, regexp)
                self.assertNotRegexpMatches(text, other_re, details)
                no_match = re.match(other_re, text)
                self.assertEqual(no_match, None, details)
        if CHECK_RE_LISTED:
            self.assertTrue(found)

    def test_var_name(self):
        """Test VAR_NAME."""
        regex = r"^" + re.VAR_NAME + r"$"
        real_names = set(locals().keys()) | set(globals().keys())
        names = ['a', 'a1', '_a1', 'aa_bb'] + list(real_names)
        for name in names:
            self.assertRegexpMatches(name, regex)
        for name in ['1a']:
            self.assertNotRegexpMatches(name, regex)

    def test_attr_name(self):
        """Test ATTR_NAME."""
        regex = r"^" + re.ATTR_NAME + r"$"
        real_attrs = set(att
                         for o in get_subclasses(object)
                         for att in dir(o))
        attrs = ['do_stuff', '__magic__'] + list(real_attrs)
        for attr in attrs:
            self.assertRegexpMatches(attr, regex)
        for attr in ['1a']:
            self.assertNotRegexpMatches(attr, regex)

    def test_type_name(self):
        """Test TYPE_NAME."""
        regex = r"^" + re.TYPE_NAME + r"$"
        real_types = set(c.__name__ for c in get_subclasses(object))
        types = ['str', 'int', 'method-wrapper'] + list(real_types)
        for type_ in types:
            self.assertRegexpMatches(type_, regex)

    def test_func_name(self):
        """Test FUNC_NAME."""
        regex = r"^" + re.FUNC_NAME + r"$"
        real_funcs = [lambda x:x, range, dir, dict.get, classmethod]  # TODO
        real_func_names = [f.__name__ for f in real_funcs]
        funcs = ['get', 'range', '<lambda>', 'print'] + list(real_func_names)
        for func in funcs:
            self.assertRegexpMatches(func, regex)

    def test_module_name(self):
        """Test MODULE_NAME."""
        regex = r"^" + re.MODULE_NAME + r"$"
        real_modules = set(sys.modules.keys())
        modules = ['sys', 'unittest.runner'] + list(real_modules)
        for mod in modules:
            self.assertRegexpMatches(mod, regex)

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
        results = (groups, named_groups)
        for msg in msgs:
            self.re_matches(msg, re.NAMENOTDEFINED_RE, results)

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
        for groups, msgs in group_msg.items():
            _, attr = groups
            named_groups = {'attr': attr}
            results = (groups, named_groups)
            for msg in msgs:
                self.re_matches(msg, re.ATTRIBUTEERROR_RE, results)

    def test_module_attribute_error(self):
        """Test MODULEHASNOATTRIBUTE_RE."""
        # Python 3.5
        msg = "module 'some_module' has no attribute 'attri'"
        groups = ('some_module', 'attri')
        _, attr = groups
        named_groups = {'attr': attr}
        results = (groups, named_groups)
        self.re_matches(msg, re.MODULEHASNOATTRIBUTE_RE, results)

    def test_cannot_import(self):
        """Test CANNOTIMPORT_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3
            "cannot import name pie",
            # Python 3.4/3.5/PyPy/PyPy3
            "cannot import name 'pie'",
            # Python 3.7
            "cannot import name 'pie' from 'math' (/some/path)",
            "cannot import name 'pie' from 'math' (unknown location)"
        ]
        name = 'pie'
        groups = (name, )
        named_groups = {'name': name}
        results = (groups, named_groups)
        for msg in msgs:
            self.re_matches(msg, re.CANNOTIMPORT_RE, results)

    def test_no_module_named(self):
        """Test NOMODULE_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/PyPy/PyPy3
            "No module named fake_module",
            # Python 3.3/3.4/3.5
            "No module named 'fake_module'",
        ]
        groups = ('fake_module',)
        results = (groups, dict())
        for msg in msgs:
            self.re_matches(msg, re.NOMODULE_RE, results)

    def test_index_out_of_range(self):
        """Test INDEXOUTOFRANGE_RE."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "list index out of range"
        self.re_matches(msg, re.INDEXOUTOFRANGE_RE, NO_GROUP)

    def test_unsubscriptable(self):
        """Test UNSUBSCRIPTABLE_RE."""
        msgs = [
            # Python 2.6
            "'function' object is unsubscriptable",
            # Python 3.2/3.3/3.4/3.5/PyPy/PyPy3
            "'function' object is not subscriptable",
        ]
        groups = ('function',)
        results = (groups, dict())
        for msg in msgs:
            self.re_matches(msg, re.UNSUBSCRIPTABLE_RE, results)

    def test_unexpected_kw_arg(self):
        """Test UNEXPECTED_KEYWORDARG_RE."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msgs = [
            ("some_func() got an unexpected keyword argument 'a'",
                ('some_func', 'a')),
            ("<lambda>() got an unexpected keyword argument 'a'",
                ('<lambda>', 'a')),
        ]
        for msg, groups in msgs:
            func, kw_arg = groups
            named_groups = {'arg': kw_arg, 'func': func}
            results = (groups, named_groups)
            self.re_matches(msg, re.UNEXPECTED_KEYWORDARG_RE, results)

    def test_unexpected_kw_arg2(self):
        """Test UNEXPECTED_KEYWORDARG2_RE."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5
        msg = "'this_doesnt_exist' is an invalid " \
            "keyword argument for this function"
        groups = ('this_doesnt_exist', )
        kw_arg, = groups
        named_groups = {'arg': kw_arg}
        results = (groups, named_groups)
        self.re_matches(msg, re.UNEXPECTED_KEYWORDARG2_RE, results)

    def test_unexpected_kw_arg3(self):
        """Test UNEXPECTED_KEYWORDARG3_RE."""
        # PyPy/PyPy3
        msg = "invalid keyword arguments to print()"
        func = 'print'
        groups = (func, )
        named_groups = {'func': func}
        results = (groups, named_groups)
        self.re_matches(msg, re.UNEXPECTED_KEYWORDARG3_RE, results)

    def test_func_takes_no_kwarg(self):
        """Test FUNC_TAKES_NO_KEYWORDARG_RE."""
        msgs = [
            # Cython : most versions
            "get() takes no keyword arguments",
            # Cython nightly (as of 21 January 2017) - Python 3.7
            "get does not take keyword arguments",
        ]
        func = 'get'
        groups = (func, )
        named_groups = {'func': func}
        results = (groups, named_groups)
        for msg in msgs:
            self.re_matches(msg, re.FUNC_TAKES_NO_KEYWORDARG_RE, results)

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
        results = (groups, dict())
        for msg in msgs:
            self.re_matches(msg, re.UNHASHABLE_RE, results)

    def test_cannot_be_interpreted_as_integer(self):
        """Test CANNOT_BE_INTERPRETED_INT_RE."""
        msgs = {
            "'str' object cannot be interpreted as an integer": 'str',
            "'list' object cannot be interpreted as an integer": 'list',
        }
        for msg, typ in msgs.items():
            results = ((typ,), dict())
            self.re_matches(msg, re.CANNOT_BE_INTERPRETED_INT_RE, results)

    def test_int_expected_got(self):
        """Test INTEGER_EXPECTED_GOT_RE."""
        msgs = {
            "expected integer, got str object": 'str',
            "range() integer end argument expected, got list.": 'list',
            "range() integer start argument expected, got list.": 'list',
        }
        for msg, typ in msgs.items():
            results = ((typ,), dict())
            self.re_matches(msg, re.INTEGER_EXPECTED_GOT_RE, results)

    def test_indices_must_be_int(self):
        """Test INDICES_MUST_BE_INT_RE."""
        msgs = {
            # Python 2.6, 2.7, 3.2, 3.3, 3.4
            "list indices must be integers, not str": "str",
            "list indices must be integers or slices, not str": "str",
            # Python 3.5
            "tuple indices must be integers or slices, not str": "str",
            # PyPy
            "list index must be an integer, not str": "str",
        }
        for msg, typ in msgs.items():
            results = ((typ,), dict())
            self.re_matches(msg, re.INDICES_MUST_BE_INT_RE, results)

    def test_outside_function(self):
        """Test OUTSIDE_FUNCTION_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
            "'return' outside function",
            # PyPy/PyPy3
            "return outside function",
        ]
        groups = ('return',)
        results = (groups, dict())
        for msg in msgs:
            self.re_matches(msg, re.OUTSIDE_FUNCTION_RE, results)

    def test_nb_positional_argument(self):
        """Test NB_ARG_RE."""
        msgs = [
            # Python 2.6/2.7/PyPy/PyPy3
            ("some_func() takes exactly 1 argument (2 given)",
                'some_func', '1', '2'),
            ("some_func() takes exactly 3 arguments (1 given)",
                'some_func', '3', '1'),
            ("some_func() takes no arguments (1 given)",
                'some_func', 'no', '1'),
            ("some_func() takes at least 2 non-keyword arguments (0 given)",
                'some_func', '2', '0'),
            # Python 3.2
            ("some_func() takes exactly 1 positional argument (2 given)",
                'some_func', '1', '2'),
            # Python 3.3/3.4/3.5
            ("some_func() takes 1 positional argument but 2 were given",
                'some_func', '1', '2'),
            ("some_func() takes 0 positional arguments but 1 was given",
                'some_func', '0', '1'),
            # PyPy adds suggestions sometimes:
            ("some_func() takes no arguments (1 given)"
             ". Did you forget 'self' in the function definition?",
                'some_func', 'no', '1'),
            # More!!!
            ("get expected at least 1 arguments, got 0",
                'get', '1', '0'),
            ("get expected at most 2 arguments, got 3",
                'get', '2', '3'),
        ]
        for msg, func, exp, nb in msgs:
            groups = (func, exp, nb)
            named_groups = {'func': func, 'expected': exp, 'actual': nb}
            results = (groups, named_groups)
            self.re_matches(msg, re.NB_ARG_RE, results)

    def test_missing_positional_arg(self):
        """Test MISSING_POS_ARG_RE."""
        msgs = [
            # Python 3.3/3.4/3.5
            "some_func() missing 2 required positional arguments: "
            "'much' and 'args'",
            "some_func() missing 1 required positional argument: "
            "'much'",
        ]
        func = 'some_func'
        groups = (func,)
        named_groups = {'func': func}
        results = (groups, named_groups)
        for msg in msgs:
            self.re_matches(msg, re.MISSING_POS_ARG_RE, results)

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
        func = 'exec'
        groups = (func,)
        named_groups = {'func': func}
        results = (groups, named_groups)
        self.re_matches(msg, re.MISSING_PARENT_RE, results)

    def test_invalid_literal(self):
        """Test INVALID_LITERAL_RE."""
        # Python 2.6/2.7/3.2/3.3/3.4/3.5/PyPy/PyPy3
        msg = "invalid literal for int() with base 10: 'toto'"
        groups = ('int', 'toto')
        results = (groups, dict())
        self.re_matches(msg, re.INVALID_LITERAL_RE, results)

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
        results = (groups, dict())
        self.re_matches(msg, re.EXPECTED_LENGTH_RE, results)

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
        results = (groups, dict())
        self.re_matches(msg, re.FUTURE_FEATURE_NOT_DEF_RE, results)

    def test_result_has_too_many_items(self):
        """Test RESULT_TOO_MANY_ITEMS_RE."""
        # Python 2.6
        msg = "range() result has too many items"
        func = 'range'
        groups = (func, )
        named_groups = {'func': func}
        results = (groups, named_groups)
        self.re_matches(msg, re.RESULT_TOO_MANY_ITEMS_RE, results)

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
        msgs = [
            ("'range' object does not support item assignment",
                ("range", "item assignment")),
            ("'str' object doesn't support item deletion",
                ("str", "item deletion")),
            ("'set' object does not support indexing",
                ("set", "indexing")),
        ]
        for msg, groups in msgs:
            results = (groups, dict())
            self.re_matches(msg, re.OBJ_DOES_NOT_SUPPORT_RE, results)

    def test_cant_convert(self):
        """Test CANT_CONVERT_RE."""
        msg = "Can't convert 'int' object to str implicitly"
        groups = ('int', 'str')
        results = (groups, dict())
        self.re_matches(msg, re.CANT_CONVERT_RE, results)

    def test_must_be_type1_not_type2(self):
        """Test MUST_BE_TYPE1_NOT_TYPE2_RE."""
        msg = "must be str, not int"
        groups = ('str', 'int')
        results = (groups, dict())
        self.re_matches(msg, re.MUST_BE_TYPE1_NOT_TYPE2_RE, results)

    def test_cannot_concat(self):
        """Test CANNOT_CONCAT_RE."""
        msg = "cannot concatenate 'str' and 'int' objects"
        groups = ('str', 'int')
        results = (groups, dict())
        self.re_matches(msg, re.CANNOT_CONCAT_RE, results)

    def test_only_concat(self):
        """Test ONLY_CONCAT_RE."""
        msg = 'can only concatenate list (not "set") to list'
        self.re_matches(msg, re.ONLY_CONCAT_RE, NO_GROUP)

    def test_unsupported_operand(self):
        """Test UNSUPPORTED_OP_RE."""
        msg = "unsupported operand type(s) for +: 'int' and 'str'"
        groups = ('+', 'int', 'str')
        results = (groups, dict())
        self.re_matches(msg, re.UNSUPPORTED_OP_RE, results)

    def test_bad_operand_unary(self):
        """Test BAD_OPERAND_UNARY_RE."""
        msgs = [
            ("bad operand type for unary ~: 'set'", ('~', 'set')),
            ("bad operand type for abs(): 'set'", ('abs()', 'set')),
            ("unsupported operand type for unary neg: 'Foobar'",
                ('neg', 'Foobar')),
        ]
        for msg, groups in msgs:
            results = (groups, dict())
            self.re_matches(msg, re.BAD_OPERAND_UNARY_RE, results)

    def test_not_callable(self):
        """Test NOT_CALLABLE_RE."""
        msg = "'list' object is not callable"
        groups = ('list',)
        results = (groups, dict())
        self.re_matches(msg, re.NOT_CALLABLE_RE, results)

    def test_descriptor_requires(self):
        """Test DESCRIPT_REQUIRES_TYPE_RE."""
        msg = "descriptor 'add' requires a 'set' object but received a 'int'"
        groups = ('add', 'set', 'int')
        results = (groups, dict())
        self.re_matches(msg, re.DESCRIPT_REQUIRES_TYPE_RE, results)

    def test_argument_not_iterable(self):
        """Test ARG_NOT_ITERABLE_RE."""
        msgs = [
            # Python 2.6/2.7/3.2/3.3/3.4/3.5
            "argument of type 'type' is not iterable",
            # PyPy/PyPy3
            "'type' object is not iterable"
        ]
        groups = ('type',)
        results = (groups, dict())
        for msg in msgs:
            self.re_matches(msg, re.ARG_NOT_ITERABLE_RE, results)

    def test_must_be_called_with_instance(self):
        """Test MUST_BE_CALLED_WITH_INST_RE."""
        msg = "unbound method add() must be called with set " \
              "instance as first argument (got int instance instead)"
        groups = ('add', 'set', 'int')
        results = (groups, dict())
        self.re_matches(msg, re.MUST_BE_CALLED_WITH_INST_RE, results)

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
            results = (groups, dict())
            self.re_matches(msg, re.OBJECT_HAS_NO_FUNC_RE, results)

    def test_instance_has_no_meth(self):
        """Test INSTANCE_HAS_NO_METH_RE."""
        # Python 2.6/2.7
        msg = "CustomClass instance has no __call__ method"
        class_, method = 'CustomClass', '__call__'
        groups = (class_, method)
        results = (groups, dict())
        self.re_matches(msg, re.INSTANCE_HAS_NO_METH_RE, results)

    def test_nobinding_nonlocal(self):
        """Test NO_BINDING_NONLOCAL_RE."""
        msg = "no binding for nonlocal 'foo' found"
        groups = ('foo',)
        results = (groups, dict())
        self.re_matches(msg, re.NO_BINDING_NONLOCAL_RE, results)

    def test_nonlocal_at_module_level(self):
        """Test NONLOCAL_AT_MODULE_RE."""
        msg = "nonlocal declaration not allowed at module level"
        self.re_matches(msg, re.NONLOCAL_AT_MODULE_RE, NO_GROUP)

    def test_unexpected_eof(self):
        """Test UNEXPECTED_EOF_RE."""
        msg = "unexpected EOF while parsing"
        self.re_matches(msg, re.UNEXPECTED_EOF_RE, NO_GROUP)

    def test_nosuchfile(self):
        """Test NO_SUCH_FILE_RE."""
        msg = "No such file or directory"
        self.re_matches(msg, re.NO_SUCH_FILE_RE, NO_GROUP)

    def test_timedata_does_not_match_format(self):
        """Test TIME_DATA_DOES_NOT_MATCH_FORMAT_RE."""
        msg = "time data '%d %b %y' does not match format '30 Nov 00'"
        # 'time data "%d \'%b %y" does not match format \'30 Nov 00\''
        groups = ("'%d %b %y'", "'30 Nov 00'")
        named_groups = {'format': "'30 Nov 00'", 'timedata': "'%d %b %y'"}
        results = (groups, named_groups)
        self.re_matches(msg, re.TIME_DATA_DOES_NOT_MATCH_FORMAT_RE, results)

    def test_invalid_token(self):
        """Test INVALID_TOKEN_RE."""
        msg = 'invalid token'
        self.re_matches(msg, re.INVALID_TOKEN_RE, NO_GROUP)

    def test_exc_must_derive_from(self):
        """Test EXC_MUST_DERIVE_FROM_RE."""
        msgs = [
            # Python 2.7
            "exceptions must be old-style classes or derived from "
            "BaseException, not NoneType",
            # Python 3.3 / 3.4
            "exceptions must derive from BaseException",
        ]
        for msg in msgs:
            self.re_matches(msg, re.EXC_MUST_DERIVE_FROM_RE, NO_GROUP)

    def test_unorderable_types(self):
        """Test UNORDERABLE_TYPES_RE."""
        msgs = [
            # Python 3.2 to 3.5
            "unorderable types: str() > int()",
            "unorderable types: FoobarClass() <= int()",
            # PyPy
            "unorderable types: FoobarClass > FoobarClass",
        ]
        for msg in msgs:
            self.re_matches(msg, re.UNORDERABLE_TYPES_RE, NO_GROUP)

    def test_op_not_supported_between_instances(self):
        """Test OP_NOT_SUPP_BETWEEN_INSTANCES_RE."""
        msgs = [
            # Python 3.6
            "'<' not supported between instances of 'int' and 'NoneType'",
            "'>' not supported between instances of 'Foo' and 'Foo'",
        ]
        for msg in msgs:
            self.re_matches(msg, re.OP_NOT_SUPP_BETWEEN_INSTANCES_RE, NO_GROUP)

    def test_max_recursion_depth(self):
        """Test MAX_RECURSION_DEPTH_RE."""
        msg = 'maximum recursion depth exceeded'
        self.re_matches(msg, re.MAX_RECURSION_DEPTH_RE, NO_GROUP)

    def test_size_changed_during_iter(self):
        """Test SIZE_CHANGED_DURING_ITER_RE."""
        msgs = {
            "Set": "Set changed size during iteration",
            "dictionnary": "dictionnary changed size during iteration",
        }
        for name, msg in msgs.items():
            groups = (name, )
            results = (groups, dict())
            self.re_matches(msg, re.SIZE_CHANGED_DURING_ITER_RE, results)

if __name__ == '__main__':
    print(sys.version_info)
    unittest2.main()
