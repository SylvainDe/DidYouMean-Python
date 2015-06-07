# -*- coding: utf-8
"""Regular expressions to parse error messages."""
import re


UNBOUNDERROR_RE = r"^local variable '(?P<name>\w+)' " \
    r"referenced before assignment$"
NAMENOTDEFINED_RE = r"^(?:global )?name '(?P<name>\w+)' is not defined$"
ATTRIBUTEERROR_RE = r"^(?:class |type object )?'?([\w\.]+)'? " \
    r"(?:object |instance )?has no attribute '(\w+)'$"
MODULEHASNOATTRIBUTE_RE = r"^module '?([\w\.]+)' has no attribute '(\w+)'$"
UNSUBSCRIBTABLE_RE = r"^'(\w+)' object " \
    r"(?:is (?:not |un)subscriptable|has no attribute '__getitem__')$"
UNEXPECTED_KEYWORDARG_RE = r"^(\w+)\(\) " \
    r"got an unexpected keyword argument '(\w+)'$"
NOMODULE_RE = r"^No module named '?(\w+)'?$"
CANNOTIMPORT_RE = r"^cannot import name '?(\w+)'?$"
INDEXOUTOFRANGE_RE = r"^list index out of range$"
ZERO_LEN_FIELD_RE = r"^zero length field name in format$"
MATH_DOMAIN_ERROR_RE = r"^math domain error$"
TOO_MANY_VALUES_UNPACK_RE = r"^too many values " \
    r"to unpack(?: \(expected \d+\))?$"
OUTSIDE_FUNCTION_RE = r"^'?(\w+)'? outside function$"
NEED_MORE_VALUES_RE = r"^(?:need more than \d+|not enough) values to unpack" \
    r"(?: \(expected \d+, got \d+\))?$"
UNHASHABLE_RE = r"^(?:unhashable type: )?'(\w+)'(?: objects are unhashable)?$"
MISSING_PARENT_RE = r"^Missing parentheses in call to '(\w+)'$"
INVALID_LITERAL_RE = r"^invalid literal for (\w+)\(\) with base \d+: '(\w+)'$"
NB_ARG_RE = r"^(\w+)\(\) takes (?:exactly )?(?:no|\d+) " \
    r"(?:positional )?arguments? \(?(?:but )?\d+ (?:were |was )?given\)?$"
MISSING_POS_ARG_RE = r"^(\w+)\(\) missing \d+ required positional " \
    r"arguments?: .*$"
INVALID_SYNTAX_RE = r"^invalid syntax$"
INVALID_COMP_RE = r"^invalid comparison$"
EXPECTED_LENGTH_RE = r"^expected length (\d+), got (\d+)$"
FUTURE_FIRST_RE = r"^(?:from )?__future__ (?:imports|statements) must " \
    r"(?:occur|appear) at (?:the )?beginning of (?:the )?file$"
FUTURE_FEATURE_NOT_DEF_RE = r"^future feature (\w+) is not defined$"
RESULT_TOO_MANY_ITEMS_RE = r"^(\w+)\(\) result has too many items$"
UNQUALIFIED_EXEC_RE = r"^unqualified exec is not allowed in function '\w+' " \
    r"(?:because )?it" \
    r" (?:is a nested function|" \
    r"contains a nested function with free variables)$"
IMPORTSTAR_RE = r"^import \* (?:only allowed at module level|" \
    r"is not allowed in function '\w+' because it (?:is )?" \
    r"(?:is a nested function|" \
    r"(?:)contains a nested function with free variables))$"
UNSUPPORTED_OP_RE = r"^unsupported operand type\(s\) for (.*): " \
    r"'(\w+)' and '(\w+)'$"
OBJ_DOES_NOT_SUPPORT_RE = r"^\'(\w+)\' object does not support " \
    r"item assignment$"
CANNOT_CONCAT_RE = r"^cannot concatenate '(\w+)' and '(\w+)' objects$"
CANT_CONVERT_RE = r"Can't convert '(\w+)' object to (\w+) implicitly$"
NOT_CALLABLE_RE = r"^'(\w+)' object is not callable$"
DESCRIPT_REQUIRES_TYPE_RE = r"^descriptor '(\w+)' requires a '(\w+)' " \
    r"object but received a '(\w+)'$"
ARG_NOT_ITERABLE_RE = r"^(?:argument of type )?'(\w+)'" \
    r"(?: object)? is not iterable$"
MUST_BE_CALLED_WITH_INST_RE = r"^unbound method (\w+)\(\) must be called " \
    r"with (\w+) instance as first argument \(got (\w+) instance instead\)$"


def match(pattern, string):
    """ Wrapper around re.match to be able to import this module as re
    without having name collisions."""
    return re.match(pattern, string)
