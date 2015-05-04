# -*- coding: utf-8
"""Logic to add suggestions to exceptions."""
import keyword
import difflib
import re
import itertools
from collections import namedtuple
from didyoumean_re import UNBOUNDERROR_RE, NAMENOTDEFINED_RE,\
    ATTRIBUTEERROR_RE, UNSUBSCRIBTABLE_RE, UNEXPECTED_KEYWORDARG_RE,\
    NOMODULE_RE, CANNOTIMPORT_RE, INVALID_COMP_RE, OUTSIDE_FUNCTION_RE,\
    FUTURE_FEATURE_NOT_DEF_RE, RESULT_TOO_MANY_ITEMS, ZERO_LEN_FIELD_RE

#: Standard modules we'll consider while searching for undefined values
# To be completed
STAND_MODULES = set(['string', 'os', 'sys', 're', 'math', 'random',
                     'datetime', 'timeit', 'unittest', 'itertools',
                     'functools', 'collections', '__future__'])

#: Almost synonyms methods that can be confused from one type to another
# To be completed
SYNONYMS_SETS = [set(['add', 'append']), set(['extend', 'update'])]


# Helper function for string manipulation
def quote(string):
    """Surround string with single quotes."""
    return "'%s'" % string


def get_close_matches(word, possibilities):
    """Wrapper around difflib.get_close_matches() to be able to
    change default values or implementation details easily."""
    return difflib.get_close_matches(word, possibilities, 3, 0.7)


def get_suggestion_string(sugg):
    """Return the suggestion list as a string."""
    sugg = list(sugg)
    return ". Did you mean " + ", ".join(sugg) + "?" if sugg else ""


# Helper functions for code introspection
def merge_dict(*dicts):
    """Merge dicts and return a dictionnary mapping key to list of values.
    Order of the values corresponds to the order of the original dicts."""
    ret = dict()
    for dict_ in dicts:
        for key, val in dict_.items():
            ret.setdefault(key, []).append(val)
    return ret

ScopedObj = namedtuple('ScopedObj', 'obj scope')


def add_scope_to_dict(dict_, scope):
    """ Convert name:obj dict to name:ScopedObj(obj,scope) dict."""
    return dict((k, ScopedObj(v, scope)) for k, v in dict_.items())


def get_objects_in_frame(frame):
    """Get objects defined in a given frame.
    This includes variable, types, builtins, etc."""
    return merge_dict(  # LEGB Rule (missing E atm - not sure if a problem)
        add_scope_to_dict(frame.f_locals, 'local'),
        add_scope_to_dict(frame.f_globals, 'global'),
        add_scope_to_dict(frame.f_builtins, 'builtin'),
    )


def import_from_frame(module_name, frame):
    """Wrapper around import to use information from frame."""
    return __import__(
        module_name,
        frame.f_globals,
        frame.f_locals)


# Debug functions
def debug_traceback(traceback):
    """Print information from the traceback for debugging purposes."""
    while traceback:
        frame = traceback.tb_frame
        if not traceback.tb_next:
            assert traceback.tb_lineno == frame.f_lineno
            assert traceback.tb_lasti == frame.f_lasti
        print(traceback,
              traceback.tb_lasti,
              frame.f_lasti,
              traceback.tb_lineno,
              frame.f_lineno,
              frame.f_code.co_name,
              frame.f_code.co_names)
        traceback = traceback.tb_next


# Functions related to NameError
def get_name_error_sugg(value, frame):
    """Get suggestions for NameError exception."""
    assert isinstance(value, NameError)
    assert len(value.args) == 1
    error_msg, = value.args
    error_re = UNBOUNDERROR_RE if isinstance(value, UnboundLocalError) \
        else NAMENOTDEFINED_RE
    match = re.match(error_re, error_msg)
    if match:
        name, = match.groups()
        return get_name_suggestions(name, frame)
    return []


def get_name_suggestions(name, frame):
    """Get the suggestions for name in case of NameError."""
    objs = get_objects_in_frame(frame)
    return itertools.chain(
        suggest_name_as_attribute(name, objs),
        suggest_name_as_standard_module(name),
        suggest_name_as_name_typo(name, objs),
        suggest_name_as_keyword_typo(name),
        suggest_name_as_missing_import(name, objs, frame),
        suggest_name_as_special_case(name))


def suggest_name_as_attribute(name, objdict):
    """Suggest that name could be an attribute of an object.
    Example: 'do_stuff()' -> 'self.do_stuff()'."""
    for nameobj, objs in objdict.items():
        prev_scope = None
        for obj, scope in objs:
            if hasattr(obj, name):
                yield quote(nameobj + '.' + name) + \
                    ('' if prev_scope is None else
                     ' (%s hidden by %s)' % (scope, prev_scope))
                break
            prev_scope = scope


def suggest_name_as_missing_import(name, objdict, frame):
    """Suggest that name could come from missing import.
    Example: 'foo' -> 'import mod, mod.foo'."""
    for mod in STAND_MODULES:
        if mod not in objdict and name in dir(import_from_frame(mod, frame)):
            yield "'%s' from %s (not imported)" % (name, mod)


def suggest_name_as_standard_module(name):
    """Suggest that name could be a non-imported standard module.
    Example: 'os.whatever' -> 'import os' and then 'os.whatever'."""
    if name in STAND_MODULES:
        yield 'to import %s first' % name


def suggest_name_as_name_typo(name, objdict):
    """Suggest that name could be a typo (misspelled existing name).
    Example: 'foobaf' -> 'foobar'."""
    for n in get_close_matches(name, objdict.keys()):
        yield quote(n) + ' (' + objdict[n][0].scope + ')'


def suggest_name_as_keyword_typo(name):
    """Suggest that name could be a typo (misspelled keyword).
    Example: 'yieldd' -> 'yield'."""
    for n in get_close_matches(name, keyword.kwlist):
        yield quote(n) + " (keyword)"


def suggest_name_as_special_case(name):
    """ Suggest that name could correspond to a typo with special handling."""
    # Imaginary unit is '1j' in Python
    if name == 'i' or name == 'j':
        yield quote('1j') + " (imaginary unit)"


# Functions related to AttributeError
def get_attribute_error_sugg(value, frame):
    """Get suggestions for AttributeError exception."""
    assert isinstance(value, AttributeError)
    assert len(value.args) == 1
    error_msg, = value.args
    match = re.match(ATTRIBUTEERROR_RE, error_msg)
    if match:
        type_str, attr = match.groups()
        return get_attribute_suggestions(type_str, attr, frame)
    return []


def get_attribute_suggestions(type_str, attribute, frame):
    """Get the suggestions closest to the attribute name for a given type."""
    objs = get_objects_in_frame(frame)
    if type_str == 'module':
        # For module, we want to get the actual name of the module
        module_name = frame.f_code.co_names[0]
        mod = objs[module_name][0].obj
        attributes = set(dir(mod))
    elif type_str in objs:
        # it kind of sucks that we retrieve the representation of the
        # type (as in 'str(type(whatever))' which might not be a known
        # name.
        obj = objs[type_str][0].obj
        attributes = set(dir(obj))
    else:  # could/should be more precise
        attributes = set()

    return itertools.chain(
        suggest_attribute_as_builtin(attribute, type_str, frame),
        suggest_attribute_as_removed(attribute, type_str, attributes),
        suggest_attribute_synonyms(attribute, attributes),
        suggest_attribute_as_typo(attribute, attributes))


def suggest_attribute_as_builtin(attribute, type_str, frame):
    """Suggest that a builtin was used as an attribute.
    Example: 'lst.len()' -> 'len(lst)'."""
    if attribute in frame.f_builtins:
        yield quote(attribute + '(' + type_str + ')')


def suggest_attribute_as_removed(attribute, type_str, attributes):
    """Suggest that attribute is removed (and give an alternative)."""
    if attribute == 'has_key' and '__contains__' in attributes:
        yield quote('key in ' + type_str)


def suggest_attribute_synonyms(attribute, attributes):
    """Suggest that a method with a similar meaning was used.
    Example: 'lst.add(e)' -> 'lst.append(e)'."""
    for set_sub in SYNONYMS_SETS:
        if attribute in set_sub:
            for syn in set_sub & attributes:
                yield quote(syn)


def suggest_attribute_as_typo(attribute, attributes):
    """Suggest the attribute could be a typo.
    Example: 'a.do_baf()' -> 'a.do_bar()'."""
    for n in get_close_matches(attribute, attributes):
        yield quote(n)


# Functions related to ImportError
def get_import_error_sugg(value, frame):
    """Get suggestions for ImportError exception."""
    assert isinstance(value, ImportError)
    assert len(value.args) == 1
    error_msg, = value.args
    match = re.match(NOMODULE_RE, error_msg)
    if match:
        module_str, = match.groups()
        return get_module_name_suggestion(module_str)
    match = re.match(CANNOTIMPORT_RE, error_msg)
    if match:
        imported_name, = match.groups()
        return get_imported_name_suggestion(imported_name, frame)
    return []


def get_module_name_suggestion(module_str):
    """Get the suggestions closest to the failing module import.
    Example: 'import maths' -> 'import math'."""
    for n in get_close_matches(module_str, STAND_MODULES):
        yield quote(n)


def get_imported_name_suggestion(imported_name, frame):
    """Get the suggestions closest to the failing import."""
    module_name = frame.f_code.co_names[0]
    return itertools.chain(
        suggest_imported_name_as_typo(imported_name, module_name, frame),
        suggest_import_from_module(imported_name, frame))


def suggest_imported_name_as_typo(imported_name, module_name, frame):
    """Suggest that imported name could be a typo from actual name in module.
    Example: 'from math import pie' -> 'from math import pi'."""
    dir_mod = dir(import_from_frame(module_name, frame))
    for n in get_close_matches(imported_name, dir_mod):
        yield quote(n)


def suggest_import_from_module(imported_name, frame):
    """Suggest than name could be found in a standard module.
    Example: 'from itertools import pi' -> 'from math import pi'."""
    for mod in STAND_MODULES:
        if imported_name in dir(import_from_frame(mod, frame)):
            yield quote('from %s import %s' % (mod, imported_name))


# Functions related to TypeError
def get_type_error_sugg(value, frame):
    """Get suggestions for TypeError exception."""
    assert isinstance(value, TypeError)
    assert len(value.args) == 1
    error_msg, = value.args
    match = re.match(UNSUBSCRIBTABLE_RE, error_msg)
    if match:  # It could be cool to extract relevant info from the trace
        type_str, = match.groups()
        if type_str == 'function':
            yield quote(type_str + '(value)')
    else:
        match = re.match(UNEXPECTED_KEYWORDARG_RE, error_msg)
        if match:
            func_name, kw_arg = match.groups()
            objs = get_objects_in_frame(frame)
            func = objs[func_name][0].obj
            args = func.__code__.co_varnames
            for n in get_close_matches(kw_arg, args):
                yield quote(n)


# Functions related to ValueError
def get_value_error_sugg(value, _):
    """Get suggestions for ValueError exception."""
    assert isinstance(value, ValueError)
    assert len(value.args) == 1
    error_msg, = value.args
    match = re.match(ZERO_LEN_FIELD_RE, error_msg)
    if match:
        yield '{0}'


# Functions related to SyntaxError
def get_syntax_error_sugg(value, frame):
    """Get suggestions for SyntaxError exception."""
    assert isinstance(value, SyntaxError)
    error_msg = value.args[0]
    match = re.match(OUTSIDE_FUNCTION_RE, error_msg)
    if match:
        yield "to indent it"
        word, = match.groups()
        if word == 'return':
            yield "'sys.exit([arg])'"
    match = re.match(FUTURE_FEATURE_NOT_DEF_RE, error_msg)
    if match:
        feature, = match.groups()
        for m in suggest_imported_name_as_typo(feature, '__future__', frame):
            yield m
    match = re.match(INVALID_COMP_RE, error_msg)
    if match:
        yield quote('!=')
    offset = value.offset
    if offset is not None and offset > 2:
        two_last = value.text[offset - 2:offset]
        if two_last == '<>':
            yield quote('!=')


# Functions related to MemoryError
def get_memory_error_sugg(value, frame):
    """Get suggestions for MemoryError exception."""
    assert isinstance(value, MemoryError)
    objs = get_objects_in_frame(frame)
    for name in frame.f_code.co_names:
        for sugg in suggest_memory_friendly_equi(name):
            if sugg in objs:
                yield quote(sugg)


# Functions related to OverflowError
def get_overflow_error_sugg(value, frame):
    """Get suggestions for OverflowError exception."""
    assert isinstance(value, OverflowError)
    objs = get_objects_in_frame(frame)
    error_msg = value.args[0]
    match = re.match(RESULT_TOO_MANY_ITEMS, error_msg)
    if match:
        func, = match.groups()
        for sugg in suggest_memory_friendly_equi(func):
            if sugg in objs:
                yield quote(sugg)


def suggest_memory_friendly_equi(name):
    """ Suggest name of a memory friendly equivalent for a function. """
    suggs = {'range': ['xrange']}
    return suggs.get(name, [])


def get_suggestions_for_exception(value, traceback):
    """Get suggestions for an exception."""
    frame = get_last_frame(traceback)
    error_types = {
        NameError: get_name_error_sugg,
        AttributeError: get_attribute_error_sugg,
        TypeError: get_type_error_sugg,
        ValueError: get_value_error_sugg,
        ImportError: get_import_error_sugg,
        SyntaxError: get_syntax_error_sugg,
        MemoryError: get_memory_error_sugg,
        OverflowError: get_overflow_error_sugg,
    }
    return itertools.chain.from_iterable(
        func(value, frame)
        for error_type, func in error_types.items()
        if isinstance(value, error_type))


def add_string_to_exception(value, string):
    """Add string to the exception parameter."""
    # The point is to have the string visible when the exception is printed
    # or converted to string - may it be via `str()`, `repr()` or when the
    # exception is uncaught and displayed (which seems to use `str()`).
    # In an ideal world, one just needs to update `args` but apparently it
    # is not enough for SyntaxError (and others?) where `msg` is to be
    # updated too (for `str()`, not for `repr()`). Also, in case of memory
    # errors (and others?), we don't have any args so we just add one.
    assert type(value.args) == tuple
    nb_args = len(value.args)
    if string:
        if nb_args:
            value.args = tuple([value.args[0] + string] + list(value.args[1:]))
            assert len(value.args) == nb_args
        else:  # adding the string anyway
            value.args = (string, )
        if hasattr(value, 'msg'):
            value.msg += string


def get_last_frame(traceback):
    """Extract last frame from a traceback."""
    if traceback is None:
        return None
    while traceback.tb_next:
        traceback = traceback.tb_next
    return traceback.tb_frame


def add_suggestions_to_exception(type_, value, traceback):
    """Add suggestion to an exception.
    Arguments are such as provided by sys.exc_info()."""
    assert isinstance(value, type_)
    add_string_to_exception(
        value,
        get_suggestion_string(
            get_suggestions_for_exception(
                value,
                traceback)))
