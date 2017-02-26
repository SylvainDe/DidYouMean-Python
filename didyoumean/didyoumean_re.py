# -*- coding: utf-8
"""Regular expressions to parse error messages."""
import re

# https://docs.python.org/3/reference/grammar.html
IDENTIFIER = r"[^\d\W]\w*"
VAR_NAME = IDENTIFIER
# This ATTR_NAME may be misleading because using getattr, any string may be
# appear in an AttributeError message. The same limitation is probably true
# for any property that can be set to pretty much any string.
# In any case, the whole point of having these pieces of regexp defined here
# is to make things easier to change if we ever have to.
ATTR_NAME = IDENTIFIER
ARG_NAME = IDENTIFIER
TYPE_NAME = r"[\w\.-]+"
MODULE_NAME = r"[\w\.]+"
FUNC_NAME = r"<?\w+>?"
VARREFBEFOREASSIGN_RE = r"^(?:local|free) variable '(?P<name>{0})' " \
    r"referenced before assignment(?: in enclosing scope)?$".format(VAR_NAME)
NAMENOTDEFINED_RE = r"^(?:global )?name '(?P<name>{0})' " \
    r"is not defined$".format(VAR_NAME)
ATTRIBUTEERROR_RE = r"^(?:class |type object )?'?({0})'? " \
    r"(?:object |instance )?has no attribute " \
    r"'(?P<attr>{1})'$".format(TYPE_NAME, ATTR_NAME)
MODULEHASNOATTRIBUTE_RE = r"^module '?({0})' has no attribute " \
    r"'(?P<attr>{1})'$".format(MODULE_NAME, ATTR_NAME)
UNSUBSCRIPTABLE_RE = r"^'({0})' object " \
    r"(?:is (?:not |un)subscriptable)$".format(TYPE_NAME)
CANNOT_BE_INTERPRETED_INT_RE = r"^'({0})' object cannot be interpreted " \
    r"as an integer$".format(TYPE_NAME)
INTEGER_EXPECTED_GOT_RE = r"^" \
    r"(?:range\(\) integer \w+ argument expected|expected integer), " \
    r"got ({0})(?: object|\.)$".format(TYPE_NAME)
INDICES_MUST_BE_INT_RE = "^{0} ind(?:ices|ex)? must be " \
    r"(?:an integer|integers)(?: or slices)?, not ({0})$".format(TYPE_NAME)
UNEXPECTED_KEYWORDARG_RE = r"^(?P<func>{1})\(\) " \
    r"got an unexpected keyword argument " \
    r"'(?P<arg>{0})'$".format(ARG_NAME, FUNC_NAME)
UNEXPECTED_KEYWORDARG2_RE = r"^'(?P<arg>{0})' is an " \
    r"invalid keyword argument for this function$".format(ARG_NAME)
UNEXPECTED_KEYWORDARG3_RE = r"^invalid keyword arguments to " \
    r"(?P<func>{0})\(\)$".format(FUNC_NAME)
FUNC_TAKES_NO_KEYWORDARG_RE = r"^(?P<func>{0})" \
    r"(?:\(\) takes no| does not take) keyword arguments$".format(FUNC_NAME)
NOMODULE_RE = r"^No module named '?({0})'?$".format(MODULE_NAME)
CANNOTIMPORT_RE = r"^cannot import name '?(?P<name>{0})'?" \
    r"(?: from '{1}' \(.*\))?$".format(IDENTIFIER, MODULE_NAME)
INDEXOUTOFRANGE_RE = r"^list index out of range$"
ZERO_LEN_FIELD_RE = r"^zero length field name in format$"
MATH_DOMAIN_ERROR_RE = r"^math domain error$"
TOO_MANY_VALUES_UNPACK_RE = r"^too many values " \
    r"to unpack(?: \(expected \d+\))?$"
OUTSIDE_FUNCTION_RE = r"^'?(\w+)'? outside function$"
NEED_MORE_VALUES_RE = r"^(?:need more than \d+|not enough) values to unpack" \
    r"(?: \(expected \d+, got \d+\))?$"
UNHASHABLE_RE = r"^(?:unhashable type: )?'({0})'" \
    r"(?: objects are unhashable)?$".format(TYPE_NAME)
MISSING_PARENT_RE = r"^Missing parentheses in call to " \
    r"'(?P<func>{0})'$".format(FUNC_NAME)
INVALID_LITERAL_RE = r"^invalid literal for (\w+)\(\) with base \d+: '(.*)'$"
NB_ARG_RE = r"^(?P<func>{0})(?:\(\) takes| expected) " \
    r"(?:exactly |at least |at most )?(?P<expected>no|\d+) " \
    r"(?:positional |non-keyword )?arguments?,? " \
    r"\(?(?:but |got )?(?P<actual>\d+)" \
    r"(?: were given| was given| given)?\)?" \
    r"(?:\. Did you forget 'self' in the function definition\?)?" \
    r"$".format(FUNC_NAME)
MISSING_POS_ARG_RE = r"^(?P<func>{0})\(\) missing \d+ required positional " \
    r"arguments?: .*$".format(FUNC_NAME)
INVALID_SYNTAX_RE = r"^invalid syntax$"
INVALID_COMP_RE = r"^invalid comparison$"
INVALID_TOKEN_RE = r"^invalid token$"
EXPECTED_LENGTH_RE = r"^expected length (\d+), got (\d+)$"
FUTURE_FIRST_RE = r"^(?:from )?__future__ (?:imports|statements) must " \
    r"(?:occur|appear) at (?:the )?beginning of (?:the )?file$"
FUTURE_FEATURE_NOT_DEF_RE = r"^future feature (\w+) is not defined$"
RESULT_TOO_MANY_ITEMS_RE = r"^(?P<func>{0})\(\) result has too many items" \
    r"$".format(FUNC_NAME)
UNQUALIFIED_EXEC_RE = r"^unqualified exec is not allowed in function '{0}' " \
    r"(?:because )?it" \
    r" (?:is a nested function|" \
    r"contains a nested function with free variables)$".format(FUNC_NAME)
IMPORTSTAR_RE = r"^import \* (?:only allowed at module level|" \
    r"is not allowed in function '{0}' because it (?:is )?" \
    r"(?:is a nested function|" \
    r"(?:)contains a nested function with free variables))" \
    r"$".format(FUNC_NAME)
UNSUPPORTED_OP_RE = r"^unsupported operand type\(s\) for (.*): " \
    r"'({0})' and '({0})'$".format(TYPE_NAME)
BAD_OPERAND_UNARY_RE = r"^(?:bad|unsupported) operand type for " \
    r"(?:unary )?(.*): '(.*)'$"
OBJ_DOES_NOT_SUPPORT_RE = r"^\'({0})\' object (?:does not|doesn't) support " \
    r"(.*)$".format(TYPE_NAME)
CANNOT_CONCAT_RE = r"^cannot concatenate '({0})' and '({0})' " \
    r"objects$".format(TYPE_NAME)
ONLY_CONCAT_RE = r'^can only concatenate {0} \(not "{0}"\) ' \
    r"to {0}$".format(TYPE_NAME)
CANT_CONVERT_RE = r"^Can't convert '({0})' object to ({0}) " \
    r"implicitly$".format(TYPE_NAME)
MUST_BE_TYPE1_NOT_TYPE2_RE = r"^must be ({0}), not ({0})$".format(TYPE_NAME)
NOT_CALLABLE_RE = r"^'({0})' object is not callable$".format(TYPE_NAME)
DESCRIPT_REQUIRES_TYPE_RE = r"^descriptor '(\w+)' requires a '({0})' " \
    r"object but received a '({0})'$".format(TYPE_NAME)
ARG_NOT_ITERABLE_RE = r"^(?:argument of type )?'({0})'" \
    r"(?: object)? is not iterable$".format(TYPE_NAME)
MUST_BE_CALLED_WITH_INST_RE = r"^unbound method (\w+)\(\) must be called " \
    r"with ({0}) instance as first argument " \
    r"\(got ({0}) instance instead\)$".format(TYPE_NAME)
OBJECT_HAS_NO_FUNC_RE = r"^(?:object of type )?'({0})' has no " \
    r"(\w+)(?:\(\))?$".format(TYPE_NAME)
INSTANCE_HAS_NO_METH_RE = r"^({0}) instance has no " \
    r"({1}) method$".format(TYPE_NAME, ATTR_NAME)
NO_BINDING_NONLOCAL_RE = r"^no binding for nonlocal '({0})' " \
    r"found$".format(VAR_NAME)
NONLOCAL_AT_MODULE_RE = r"^nonlocal declaration not allowed at module level$"
UNEXPECTED_EOF_RE = r"^unexpected EOF while parsing$"
NO_SUCH_FILE_RE = r"^No such file or directory$"
TIME_DATA_DOES_NOT_MATCH_FORMAT_RE = r"^time data " \
    r"(?P<timedata>.*) does not match format (?P<format>.*)$"
MAX_RECURSION_DEPTH_RE = r"^maximum recursion depth exceeded$"
SIZE_CHANGED_DURING_ITER_RE = r"^(\w+) changed size during iteration$"
EXC_MUST_DERIVE_FROM_RE = r"^exceptions must .*derive.*from.*BaseException.*$"
UNORDERABLE_TYPES_RE = r"^unorderable types: " \
        r"{0}(?:\(\))? [<=>]+ {0}(?:\(\))?$".format(TYPE_NAME)
OP_NOT_SUPP_BETWEEN_INSTANCES_RE = r"^'[<=>]+' not supported between " \
        r"instances of '{0}' and '{0}'$".format(TYPE_NAME)

ALL_REGEXPS = dict((k, v)
                   for k, v in dict(locals()).items()
                   if k.endswith('_RE'))


def match(pattern, string):
    """Wrap function from the re module.

    Wrapper around re.match to be able to import this module as re
    without having name collisions.
    """
    return re.match(pattern, string)


if __name__ == '__main__':
    for name, val in ALL_REGEXPS.items():
        if not (val.startswith('^') and val.endswith('$')):
            print("Missing ^$ for ", name)
