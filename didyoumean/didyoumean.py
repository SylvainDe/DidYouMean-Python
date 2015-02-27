# -*- coding: utf-8
"""Logic to add suggestions to exceptions."""
import keyword
import difflib
import re

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
ATTRIBUTEERROR_RE = r"^'?(\w+)'? (?:object|instance) has no attribute '(\w+)'$"
TYPEERROR_RE = r"^'(\w+)' object " \
    "(?:is (?:not |un)subscriptable|has no attribute '__getitem__')$"
NOMODULE_RE = r"^No module named '?(\w+)'?$"
CANNOTIMPORT_RE = r"^cannot import name '?(\w+)'?$"


def merge_dict(*dicts):
    """Merge dictionnaries.
    It gives priority to the beginning in case of duplicated keys()."""
    ret = dict()
    for dict_ in reversed(dicts):
        ret.update(dict_)
    return ret


def get_objects_in_frame(frame):
    """Get objects defined in a given frame.
    This includes variable, types, builtins, etc."""
    return merge_dict(  # LEGB Rule (missing E atm - not sure if a problem)
        frame.f_locals,
        frame.f_globals,
        frame.f_builtins,
    )


def get_close_matches(word, possibilities):
    """Wrapper around difflib.get_close_matches() to be able to
    change default values or implementation details easily."""
    return difflib.get_close_matches(word, possibilities)


def suggest_name_as_attribute(name, objdict):
    """Suggest that name could be an attribute of an object.
    Example: 'do_stuff()' -> 'self.do_stuff()'."""
    return [nameobj + '.' + name
            for nameobj, obj in objdict.items()
            if hasattr(obj, name)]


def suggest_name_as_standard_module(name):
    """Suggest that name could be a non-importer standard module.
    Example: 'os.whatever' -> 'import os' and then 'os.whatever'."""
    return ['import ' + name] if name in STAND_MODULES else []


def suggest_name_as_name_typo(name, objdict):
    """Suggest that name could be a typo (misspelled existing name).
    Example: 'foobaf' -> 'foobar'."""
    return get_close_matches(name, objdict.keys())


def suggest_name_as_keyword_typo(name):
    """Suggest that name could be a typo (misspelled keyword).
    Example: 'yieldd' -> 'yield'."""
    return get_close_matches(name, keyword.kwlist)


def get_name_suggestions(name, frame):
    """Get the suggestions for name in case of NameError."""
    objs = get_objects_in_frame(frame)
    return suggest_name_as_attribute(name, objs) + \
        suggest_name_as_standard_module(name) + \
        suggest_name_as_name_typo(name, objs) + \
        suggest_name_as_keyword_typo(name)


def suggest_attribute_as_builtin(attribute, type_str, frame):
    """Suggest that a builtin was used as an attribute.
    Example: 'lst.len()' -> 'len(lst)'."""
    return [attribute + '(' + type_str + ')'] \
        if attribute in frame.f_builtins else []


def suggest_attribute_synonyms(attribute, attributes):
    """Suggest that a method with a similar meaning was used.
    Example: 'lst.add(e)' -> 'lst.append(e)'."""
    return [syn
            for set_sub in SYNONYMS_SETS
            if attribute in set_sub
            for syn in set_sub & attributes]


def suggest_attribute_as_typo(attribute, attributes):
    """Suggest the attribute could be a typo.
    Example: 'a.do_baf()' -> 'a.do_bar()'."""
    return get_close_matches(attribute, attributes)


def get_attribute_suggestions(type_str, attribute, frame):
    """Get the suggestions closest to the attribute name for a given type."""
    # For module, we want to get the actual name of the module
    module_name = frame.f_code.co_names[0]
    type_or_module = module_name if type_str == 'module' else type_str
    objs = get_objects_in_frame(frame)
    attributes = set(dir(objs[type_or_module]))

    return suggest_attribute_as_builtin(attribute, type_str, frame) + \
        suggest_attribute_synonyms(attribute, attributes) + \
        suggest_attribute_as_typo(attribute, attributes)


def import_from_frame(module_name, frame):
    """Wrapper around import to use information from frame."""
    return __import__(
        module_name,
        globals=frame.f_globals,
        locals=frame.f_locals)


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
    return ['from %s import %s' % (mod, imported_name)
            for mod in STAND_MODULES
            if imported_name in dir(import_from_frame(mod, frame))]


def get_imported_name_suggestion(imported_name, frame):
    """Get the suggestions closest to the failing import."""
    return suggest_imported_name_as_typo(imported_name, frame) + \
        suggest_import_from_module(imported_name, frame)


def get_module_name_suggestion(module_str):
    """Get the suggestions closest to the failing module import.
    Example: 'import maths' -> 'import math'."""
    return get_close_matches(module_str, STAND_MODULES)


def get_suggestion_string(sugg):
    """Return the suggestion list as a string."""
    return ". Did you mean '" + "', '".join(sugg) + "'?" if sugg else ""


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


def enhance_name_error(type_, value, frame):
    """Enhance NameError exception."""
    assert issubclass(type_, NameError)
    assert len(value.args) == 1
    error_msg = value.args[0]
    error_re = UNBOUNDERROR_RE if issubclass(type_, UnboundLocalError) \
        else NAMENOTDEFINED_RE
    match = re.match(error_re, error_msg)
    assert match, "No match for %s" % error_msg
    var, = match.groups()
    sugg = get_name_suggestions(var, frame)
    value.args = (error_msg + get_suggestion_string(sugg), )
    assert len(value.args) == 1


def enhance_attribute_error(type_, value, frame):
    """Enhance AttributeError exception."""
    assert issubclass(type_, AttributeError)
    assert len(value.args) == 1
    error_msg = value.args[0]
    match = re.match(ATTRIBUTEERROR_RE, error_msg)
    assert match, "No match for %s" % error_msg
    type_str, attr = match.groups()
    sugg = get_attribute_suggestions(type_str, attr, frame)
    value.args = (error_msg + get_suggestion_string(sugg), )
    assert len(value.args) == 1


def enhance_type_error(type_, value):
    """Enhance TypeError exception."""
    assert issubclass(type_, TypeError)
    assert len(value.args) == 1
    error_msg = value.args[0]
    match = re.match(TYPEERROR_RE, error_msg)
    if match:  # It could be cool to extract relevant info from the trace
        type_str, = match.groups()
        sugg = [type_str + '(value)'] if type_str == 'function' else []
        value.args = (error_msg + get_suggestion_string(sugg), )
    assert len(value.args) == 1


def enhance_import_error(type_, value, frame):
    """Enhance ImportError exception."""
    assert issubclass(type_, ImportError)
    assert len(value.args) == 1
    error_msg = value.args[0]
    match = re.match(NOMODULE_RE, error_msg)
    if match:
        module_str, = match.groups()
        sugg = get_module_name_suggestion(module_str)
        value.args = (error_msg + get_suggestion_string(sugg), )
    else:
        match = re.match(CANNOTIMPORT_RE, error_msg)
        assert match, "No match for %s" % error_msg
        imported_name, = match.groups()
        sugg = get_imported_name_suggestion(imported_name, frame)
        value.args = (error_msg + get_suggestion_string(sugg), )
    assert len(value.args) == 1


def add_suggestions_to_exception(type_, value, traceback):
    """Add suggestion to an exception.
    Arguments are such as provided by sys.exc_info()."""
    # We care about the last element of the traceback
    end_traceback = traceback
    while end_traceback.tb_next:
        end_traceback = end_traceback.tb_next
    last_frame = end_traceback.tb_frame
    if issubclass(type_, NameError):
        enhance_name_error(type_, value, last_frame)
    elif issubclass(type_, AttributeError):
        enhance_attribute_error(type_, value, last_frame)
    elif issubclass(type_, TypeError):
        enhance_type_error(type_, value)
    elif issubclass(type_, ImportError):
        enhance_import_error(type_, value, last_frame)
    # Could be added : IndexError, KeyError
