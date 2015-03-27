# -*- coding: utf-8
"""Logic to add suggestions to exceptions."""
import keyword
import difflib
import re
import itertools

#: Standard modules we'll consider while searching for undefined values
# To be completed
STAND_MODULES = set(['string', 'os', 'sys', 're', 'math', 'random',
                     'datetime', 'timeit', 'unittest', 'itertools',
                     'functools'])

#: Almost synonyms methods that can be confused from one type to another
# To be completed
SYNONYMS_SETS = [set(['add', 'append']), set(['extend', 'update'])]

# Regular expressions to parse error messages
UNBOUNDERROR_RE = r"^local variable '(\w+)' referenced before assignment$"
NAMENOTDEFINED_RE = r"^(?:global )?name '(\w+)' is not defined$"
ATTRIBUTEERROR_RE = r"^'?([\w\.]+)'? (?:object|instance) " \
    "has no attribute '(\w+)'$"
UNSUBSCRIBTABLE_RE = r"^'(\w+)' object " \
    "(?:is (?:not |un)subscriptable|has no attribute '__getitem__')$"
NOMODULE_RE = r"^No module named '?(\w+)'?$"
CANNOTIMPORT_RE = r"^cannot import name '?(\w+)'?$"


# Helper function for string manipulation
def quote(string):
    """Surround string with single quotes."""
    return "'%s'" % string


def get_close_matches(word, possibilities):
    """Wrapper around difflib.get_close_matches() to be able to
    change default values or implementation details easily."""
    for s in difflib.get_close_matches(word, possibilities, 3, 0.7):
        yield quote(s)


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


def get_objects_in_frame(frame):
    """Get objects defined in a given frame.
    This includes variable, types, builtins, etc."""
    return merge_dict(  # LEGB Rule (missing E atm - not sure if a problem)
        frame.f_locals,
        frame.f_globals,
        frame.f_builtins,
    )


def import_from_frame(module_name, frame):
    """Wrapper around import to use information from frame."""
    return __import__(
        module_name,
        globals=frame.f_globals,
        locals=frame.f_locals)


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
def get_name_error_sugg(type_, value, frame):
    """Get suggestions for NameError exception."""
    assert issubclass(type_, NameError)
    assert len(value.args) == 1
    error_msg, = value.args
    error_re = UNBOUNDERROR_RE if issubclass(type_, UnboundLocalError) \
        else NAMENOTDEFINED_RE
    match = re.match(error_re, error_msg)
    assert match, "No match for %s" % error_msg
    name, = match.groups()
    return get_name_suggestions(name, frame)


def get_name_suggestions(name, frame):
    """Get the suggestions for name in case of NameError."""
    objs = get_objects_in_frame(frame)
    return itertools.chain(
        suggest_name_as_attribute(name, objs),
        suggest_name_as_standard_module(name),
        suggest_name_as_name_typo(name, objs),
        suggest_name_as_keyword_typo(name))


def suggest_name_as_attribute(name, objdict):
    """Suggest that name could be an attribute of an object.
    Example: 'do_stuff()' -> 'self.do_stuff()'."""
    for nameobj, objs in objdict.items():
        for i, obj in enumerate(objs):
            if hasattr(obj, name):
                yield quote(nameobj + '.' + name) + (' (hidden)' if i else '')


def suggest_name_as_standard_module(name):
    """Suggest that name could be a non-imported standard module.
    Example: 'os.whatever' -> 'import os' and then 'os.whatever'."""
    if name in STAND_MODULES:
        yield 'to import %s first' % name


def suggest_name_as_name_typo(name, objdict):
    """Suggest that name could be a typo (misspelled existing name).
    Example: 'foobaf' -> 'foobar'."""
    return get_close_matches(name, objdict.keys())


def suggest_name_as_keyword_typo(name):
    """Suggest that name could be a typo (misspelled keyword).
    Example: 'yieldd' -> 'yield'."""
    return get_close_matches(name, keyword.kwlist)


# Functions related to AttributeError
def get_attribute_error_sugg(type_, value, frame):
    """Get suggestions for AttributeError exception."""
    assert issubclass(type_, AttributeError)
    assert len(value.args) == 1
    error_msg, = value.args
    match = re.match(ATTRIBUTEERROR_RE, error_msg)
    assert match, "No match for %s" % error_msg
    type_str, attr = match.groups()
    return get_attribute_suggestions(type_str, attr, frame)


def get_attribute_suggestions(type_str, attribute, frame):
    """Get the suggestions closest to the attribute name for a given type."""
    objs = get_objects_in_frame(frame)
    if type_str == 'module':
        # For module, we want to get the actual name of the module
        module_name = frame.f_code.co_names[0]
        attributes = set(dir(objs[module_name][0]))
    elif type_str in objs:
        # it kind of sucks that we retrieve the representation of the
        # type (as in 'str(type(whatever))' which might not be a known
        # name.
        attributes = set(dir(objs[type_str][0]))
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
    return get_close_matches(attribute, attributes)


# Functions related to ImportError
def get_import_error_sugg(type_, value, frame):
    """Get suggestions for ImportError exception."""
    assert issubclass(type_, ImportError)
    assert len(value.args) == 1
    error_msg, = value.args
    match = re.match(NOMODULE_RE, error_msg)
    if match:
        module_str, = match.groups()
        return get_module_name_suggestion(module_str)
    else:
        match = re.match(CANNOTIMPORT_RE, error_msg)
        assert match, "No match for %s" % error_msg
        imported_name, = match.groups()
        return get_imported_name_suggestion(imported_name, frame)


def get_module_name_suggestion(module_str):
    """Get the suggestions closest to the failing module import.
    Example: 'import maths' -> 'import math'."""
    return get_close_matches(module_str, STAND_MODULES)


def get_imported_name_suggestion(imported_name, frame):
    """Get the suggestions closest to the failing import."""
    return itertools.chain(
        suggest_imported_name_as_typo(imported_name, frame),
        suggest_import_from_module(imported_name, frame))


def suggest_imported_name_as_typo(imported_name, frame):
    """Suggest that imported name could be a typo from actual name in module.
    Example: 'from math import pie' -> 'from math import pi'."""
    module_name = frame.f_code.co_names[0]
    return get_close_matches(
        imported_name,
        dir(import_from_frame(module_name, frame)))


def suggest_import_from_module(imported_name, frame):
    """Suggest than name could be found in a standard module.
    Example: 'from itertools import pi' -> 'from math import pi'."""
    for mod in STAND_MODULES:
        if imported_name in dir(import_from_frame(mod, frame)):
            yield quote('from %s import %s' % (mod, imported_name))


# Functions related to TypeError
def get_type_error_sugg(type_, value, frame):
    """Get suggestions for TypeError exception."""
    assert issubclass(type_, TypeError)
    assert len(value.args) == 1
    error_msg, = value.args
    match = re.match(UNSUBSCRIBTABLE_RE, error_msg)
    if match:  # It could be cool to extract relevant info from the trace
        type_str, = match.groups()
        if type_str == 'function':
            yield quote(type_str + '(value)')


# Functions related to SyntaxError
def get_syntax_error_sugg(type_, value, frame):
    """Get suggestions for SyntaxError exception."""
    assert issubclass(type_, SyntaxError)
    offset = value.offset
    if offset > 2:
        two_last = value.text[offset - 2:offset]
        if two_last == '<>':
            yield quote('!=')


# Functions related to ValueError
def get_value_error_sugg(type_, value, frame):
    """Get suggestions for ValueError exception."""
    assert issubclass(type_, ValueError)
    assert len(value.args) == 1
    error_msg, = value.args
    return []


# Functions related to IndexError
def get_index_error_sugg(type_, value, frame):
    """Get suggestions for IndexError exception."""
    assert issubclass(type_, IndexError)
    assert len(value.args) == 1
    error_msg, = value.args
    return []


# Functions related to KeyError
def get_key_error_sugg(type_, value, frame):
    """Get suggestions for KeyError exception."""
    assert issubclass(type_, KeyError)
    assert len(value.args) == 1
    error_msg, = value.args
    return []


def get_suggestions_for_exception(type_, value, frame):
    """Get suggestions for an exception."""
    error_types = {
        NameError: get_name_error_sugg,
        AttributeError: get_attribute_error_sugg,
        TypeError: get_type_error_sugg,
        ImportError: get_import_error_sugg,
        SyntaxError: get_syntax_error_sugg,
        ValueError: get_value_error_sugg,
        IndexError: get_index_error_sugg,
        KeyError: get_key_error_sugg,
    }
    return itertools.chain.from_iterable(
        func(type_, value, frame)
        for error_type, func in error_types.items()
        if issubclass(type_, error_type))


def add_string_to_exception(value, string):
    """Add string to the exception parameter."""
    assert type(value.args) == tuple
    nb_args = len(value.args)
    if string and nb_args:
        value.args = tuple([value.args[0] + string] + list(value.args[1:]))
        assert len(value.args) == nb_args


def get_last_frame(traceback):
    """Extract last frame from a traceback."""
    while traceback.tb_next:
        traceback = traceback.tb_next
    return traceback.tb_frame


def add_suggestions_to_exception(type_, value, traceback):
    """Add suggestion to an exception.
    Arguments are such as provided by sys.exc_info()."""
    add_string_to_exception(
        value,
        get_suggestion_string(
            get_suggestions_for_exception(
                type_,
                value,
                get_last_frame(traceback))))
