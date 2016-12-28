# -*- coding: utf-8
"""Regular expressions to parse error messages."""
import re


VARREFBEFOREASSIGN_RE = r"^(?:local|free) variable '(?P<name>\w+)' " \
    r"referenced before assignment(?: in enclosing scope)?$"
NAMENOTDEFINED_RE = r"^(?:global )?name '(?P<name>\w+)' is not defined$"
ATTRIBUTEERROR_RE = r"^(?:class |type object )?'?([\w\.]+)'? " \
    r"(?:object |instance )?has no attribute '(\w+)'$"
MODULEHASNOATTRIBUTE_RE = r"^module '?([\w\.]+)' has no attribute '(\w+)'$"
UNSUBSCRIPTABLE_RE = r"^'(\w+)' object " \
    r"(?:is (?:not |un)subscriptable)$"
UNEXPECTED_KEYWORDARG_RE = r"^(.+)\(\) " \
    r"got an unexpected keyword argument '(\w+)'$"
UNEXPECTED_KEYWORDARG2_RE = r"^'(\w+)' is an " \
    r"invalid keyword argument for this function$"
UNEXPECTED_KEYWORDARG3_RE = r"^invalid keyword arguments to (\w+)\(\)$"
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
NB_ARG_RE = r"^(\w+)\(\) takes (?:exactly |at least )?(no|\d+) " \
    r"(?:positional |non-keyword )?arguments? " \
    r"\(?(?:but )?(\d+) (?:were |was )?given\)?$"
MISSING_POS_ARG_RE = r"^(\w+)\(\) missing \d+ required positional " \
    r"arguments?: .*$"
INVALID_SYNTAX_RE = r"^invalid syntax$"
INVALID_COMP_RE = r"^invalid comparison$"
INVALID_TOKEN_RE = r"^invalid token$"
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
BAD_OPERAND_UNARY_RE = r"^(?:bad|unsupported) operand type for " \
    r"(?:unary )?(.*): '(.*)'$"
OBJ_DOES_NOT_SUPPORT_RE = r"^\'(\w+)\' object (?:does not|doesn't) support " \
    r"(.*)$"
CANNOT_CONCAT_RE = r"^cannot concatenate '(\w+)' and '(\w+)' objects$"
CANT_CONVERT_RE = r"^Can't convert '(\w+)' object to (\w+) implicitly$"
MUST_BE_TYPE1_NOT_TYPE2_RE = r"^must be (\w+), not (\w+)$"
NOT_CALLABLE_RE = r"^'(\w+)' object is not callable$"
DESCRIPT_REQUIRES_TYPE_RE = r"^descriptor '(\w+)' requires a '(\w+)' " \
    r"object but received a '(\w+)'$"
ARG_NOT_ITERABLE_RE = r"^(?:argument of type )?'(\w+)'" \
    r"(?: object)? is not iterable$"
MUST_BE_CALLED_WITH_INST_RE = r"^unbound method (\w+)\(\) must be called " \
    r"with (\w+) instance as first argument \(got (\w+) instance instead\)$"
OBJECT_HAS_NO_FUNC_RE = r"^(?:object of type )?'(\w+)' has no (\w+)(?:\(\))?$"
NO_BINDING_NONLOCAL_RE = r"^no binding for nonlocal '(\w+)' found$"
NONLOCAL_AT_MODULE_RE = r"^nonlocal declaration not allowed at module level$"
UNEXPECTED_EOF_RE = r"^unexpected EOF while parsing$"
NO_SUCH_FILE_RE = r"^No such file or directory$"
TIME_DATA_DOES_NOT_MATCH_FORMAT_RE = r"^time data " \
    r"(?P<timedata>.*) does not match format (?P<format>.*)$"
MAX_RECURSION_DEPTH_RE = r"^maximum recursion depth exceeded$"
SIZE_CHANGED_DURING_ITER_RE = r"^(\w+) changed size during iteration$"
EXC_MUST_DERIVE_FROM_RE = r"^exceptions must .*derive.*from.*BaseException.*$"
UNORDERABLE_TYPES_RE = r"^unorderable types: " \
        r"\w+(?:\(\))? [<=>]+ \w+(?:\(\))?$"
OP_NOT_SUPP_BETWEEN_INSTANCES_RE = r"^'[<=>]+' not supported between " \
        r"instances of '\w+' and '\w+'$"

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
