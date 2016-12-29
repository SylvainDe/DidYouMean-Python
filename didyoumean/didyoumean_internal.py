# -*- coding: utf-8
"""Logic to add suggestions to exceptions."""
import keyword
import difflib
import didyoumean_re as re
import itertools
import inspect
import errno
import os
import sys
from collections import namedtuple


#: Standard modules we'll consider while searching for symbols, for instance:
#  - NameError and the name is an attribute of a std (imported or not) module
#  - NameError and the name is the name of a standard (non imported) module
#  - ImportError and the name looks like a standard (imported or not) module
#  - TODO: AttributeError and the attribute is the one of a module
# Not that in the first case, the modules must be considered safe to import
# (no side-effects) but in some other cases, we only care about the names
# of the module and a more extended list could be used.
# The list is to be completed
# Potential candidates :
#  - sys.builtin_module_names
# https://docs.python.org/2/library/sys.html#sys.builtin_module_names
#  - sys.modules
# https://docs.python.org/2/library/sys.html#sys.modules
#  - pkgutil.iter_modules
# https://docs.python.org/2/library/pkgutil.html#pkgutil.iter_modules
STAND_MODULES = set(['string', 'os', 'sys', 're', 'math', 'random',
                     'datetime', 'timeit', 'unittest', 'itertools',
                     'functools', 'collections', '__future__'])

#: Almost synonyms methods that can be confused from one type to another
# To be completed
SYNONYMS_SETS = [set(['add', 'append']), set(['extend', 'update'])]

#: Maximum number of files suggested
MAX_NB_FILES = 4

#: Message to suggest not using recursion
AVOID_REC_MSG = \
    "to avoid recursion (cf " \
    "http://neopythonic.blogspot.fr/2009/04/tail-recursion-elimination.html)"
#: Messages for functions removed from one version to another
APPLY_REMOVED_MSG = "to call the function directly (`apply` is deprecated " \
    "since Python 2.3, removed since Python 3)"
BUFFER_REMOVED_MSG = '"memoryview" (`buffer` has been removed " \
    "since Python 3)'
CMP_REMOVED_MSG = "to use comparison operators (`cmp` is removed since " \
    "Python 3 but you can define `def cmp(a, b): return (a > b) - (a < b)` " \
    "if needed)"
CMP_ARG_REMOVED_MSG = 'to use "key" (`cmp` has been replaced by `key` ' \
    "since Python 3 - `functools.cmp_to_key` provides a convenient way " \
    "to convert cmp function to key function)"
MEMVIEW_ADDED_MSG = '"buffer" (`memoryview` is added in Python 2.7 and " \
    "completely replaces `buffer` since Python 3)'
RELOAD_REMOVED_MSG = '"importlib.reload" or "imp.reload" (`reload` is " \
    "removed since Python 3)'
STDERR_REMOVED_MSG = '"Exception" (`StandardError` has been removed since " \
    "Python 3)'


# Helper function for string manipulation
def quote(string):
    """Surround string with single quotes."""
    return "'{0}'".format(string)


def get_close_matches(word, possibilities):
    """
    Return a list of the best "good enough" matches.

    Wrapper around difflib.get_close_matches() to be able to
    change default values or implementation details easily.
    """
    return [w
            for w in difflib.get_close_matches(word, possibilities, 3, 0.7)
            if w != word]


def get_suggestion_string(sugg):
    """Return the suggestion list as a string."""
    sugg = list(sugg)
    return ". Did you mean " + ", ".join(sugg) + "?" if sugg else ""


# Helper functions for code introspection
def subclasses_wrapper(klass):
    """Wrapper around __subclass__ as it is not as easy as it should."""
    method = getattr(klass, '__subclasses__', None)
    if method is None:
        return []
    try:
        return method()
    except TypeError:
        try:
            return method(klass)
        except TypeError:
            return []


def get_subclasses(klass):
    """Get the subclasses of a class.

    Get the set of direct/indirect subclasses of a class including itself.
    """
    subclasses = set(subclasses_wrapper(klass))
    for derived in set(subclasses):
        subclasses.update(get_subclasses(derived))
    subclasses.add(klass)
    return subclasses


def get_types_for_str_using_inheritance(name):
    """Get types corresponding to a string name.

    This goes through all defined classes. Therefore, it :
    - does not include old style classes on Python 2.x
    - is to be called as late as possible to ensure wanted type is defined.
    """
    return set(c for c in get_subclasses(object) if c.__name__ == name)


def get_types_for_str_using_names(name, frame):
    """Get types corresponding to a string name using names in frame.

    This does not find everything as builtin types for instance may not
    be in the names.
    """
    return set(obj
               for obj, _ in get_objects_in_frame(frame).get(name, [])
               if inspect.isclass(obj) and obj.__name__ == name)


def get_types_for_str(tp_name, frame):
    """Get a list of candidate types from a string.

    String corresponds to the tp_name as described in :
    https://docs.python.org/2/c-api/typeobj.html#c.PyTypeObject.tp_name
    as it is the name used in exception messages. It may include full path
    with module, subpackage, package but this is just removed in current
    implementation to search only based on the type name.

    Lookup uses both class hierarchy and name lookup as the first may miss
    old style classes on Python 2 and second does find them.
    Just like get_types_for_str_using_inheritance, this needs to be called
    as late as possible but because it requires a frame, there is not much
    choice anyway.
    """
    name = tp_name.split('.')[-1]
    res = set.union(
        get_types_for_str_using_inheritance(name),
        get_types_for_str_using_names(name, frame))
    assert all(inspect.isclass(t) and t.__name__ == name for t in res)
    return res


def merge_dict(*dicts):
    """Merge dicts and return a dictionnary mapping key to list of values.

    Order of the values corresponds to the order of the original dicts.
    """
    ret = dict()
    for dict_ in dicts:
        for key, val in dict_.items():
            ret.setdefault(key, []).append(val)
    return ret

ScopedObj = namedtuple('ScopedObj', 'obj scope')


def add_scope_to_dict(dict_, scope):
    """Convert name:obj dict to name:ScopedObj(obj,scope) dict."""
    return dict((k, ScopedObj(v, scope)) for k, v in dict_.items())


def get_objects_in_frame(frame):
    """Get objects defined in a given frame.

    This includes variable, types, builtins, etc.
    The function returns a dictionnary mapping names to a (non empty)
    list of ScopedObj objects in the order following the LEGB Rule.
    """
    # https://www.python.org/dev/peps/pep-0227/ PEP227 Statically Nested Scopes
    # "Under this proposal, it will not be possible to gain dictionary-style
    #      access to all visible scopes."
    # https://www.python.org/dev/peps/pep-3104/ PEP 3104 Access to Names in
    #      Outer Scopes
    # LEGB Rule : missing E (enclosing) at the moment.
    # I'm not sure if it can be fixed but if it can, suggestions
    # tagged TODO_ENCLOSING could be implemented (and tested).
    return merge_dict(
        add_scope_to_dict(frame.f_locals, 'local'),
        add_scope_to_dict(frame.f_globals, 'global'),
        add_scope_to_dict(frame.f_builtins, 'builtin'),
    )


def import_from_frame(module_name, frame):
    """Wrapper around import to use information from frame."""
    if frame is None:
        return None
    return __import__(
        module_name,
        frame.f_globals,
        frame.f_locals)


# To be used in `get_suggestions_for_exception`.
SUGGESTION_FUNCTIONS = dict()


def register_suggestion_for(error_type, regex):
    """Decorator to register a function to be called to get suggestions.

    Parameters correspond to the fact that the registration is done for a
    specific error type and if the error message matches a given regex
    (if the regex is None, the error message is assumed to match before being
    retrieved).

    The decorated function is expected to yield any number (0 included) of
    suggestions (as string).
    The parameters are: (value, frame, groups):
     - value: Exception object
     - frame: Last frame of the traceback (may be None when the traceback is
        None which happens only in edge cases)
     - groups: Groups from the error message matched by the error message.
    """
    def internal_decorator(func):
        def registered_function(value, frame):
            if regex is None:
                return func(value, frame, [])
            error_msg = value.args[0]
            match = re.match(regex, error_msg)
            if match:
                return func(value, frame, match.groups())
            return []
        SUGGESTION_FUNCTIONS.setdefault(error_type, []) \
            .append(registered_function)
        return func  # return original function
    return internal_decorator


# Functions related to NameError
@register_suggestion_for(NameError, re.VARREFBEFOREASSIGN_RE)
@register_suggestion_for(NameError, re.NAMENOTDEFINED_RE)
def suggest_name_not_defined(value, frame, groups):
    """Get the suggestions for name in case of NameError."""
    del value  # unused param
    name, = groups
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

    Example: 'do_stuff()' -> 'self.do_stuff()'.
    """
    for nameobj, objs in objdict.items():
        prev_scope = None
        for obj, scope in objs:
            if hasattr(obj, name):
                yield quote(nameobj + '.' + name) + \
                    ('' if prev_scope is None else
                     ' ({0} hidden by {1})'.format(scope, prev_scope))
                break
            prev_scope = scope


def suggest_name_as_missing_import(name, objdict, frame):
    """Suggest that name could come from missing import.

    Example: 'foo' -> 'import mod, mod.foo'.
    """
    for mod in STAND_MODULES:
        if mod not in objdict and name in dir(import_from_frame(mod, frame)):
            yield "'{0}' from {1} (not imported)".format(name, mod)


def suggest_name_as_standard_module(name):
    """Suggest that name could be a non-imported standard module.

    Example: 'os.whatever' -> 'import os' and then 'os.whatever'.
    """
    if name in STAND_MODULES:
        yield 'to import {0} first'.format(name)


def suggest_name_as_name_typo(name, objdict):
    """Suggest that name could be a typo (misspelled existing name).

    Example: 'foobaf' -> 'foobar'.
    """
    for name in get_close_matches(name, objdict.keys()):
        yield quote(name) + ' (' + objdict[name][0].scope + ')'


def suggest_name_as_keyword_typo(name):
    """Suggest that name could be a typo (misspelled keyword).

    Example: 'yieldd' -> 'yield'.
    """
    for name in get_close_matches(name, keyword.kwlist):
        yield quote(name) + " (keyword)"


def suggest_name_as_special_case(name):
    """Suggest that name could correspond to a typo with special handling."""
    special_cases = {
        # Imaginary unit is '1j' in Python
        'i': quote('1j') + " (imaginary unit)",
        'j': quote('1j') + " (imaginary unit)",
        # Shell commands entered in interpreter
        'pwd': quote('os.getcwd()'),
        'ls': quote('os.listdir(os.getcwd())'),
        'cd': quote('os.chdir(path)'),
        'rm': "'os.remove(filename)', 'shutil.rmtree(dir)' for recursive",
        # Function removed from Python
        'apply': APPLY_REMOVED_MSG,
        'buffer': BUFFER_REMOVED_MSG,
        'cmp': CMP_REMOVED_MSG,
        'memoryview': MEMVIEW_ADDED_MSG,
        'reload': RELOAD_REMOVED_MSG,
        'StandardError': STDERR_REMOVED_MSG,
    }
    result = special_cases.get(name)
    if result is not None:
        yield result


# Functions related to AttributeError
def get_attribute_suggestions(type_str, attribute, frame):
    """Get the suggestions closest to the attribute name for a given type."""
    types = get_types_for_str(type_str, frame)
    attributes = set(a for t in types for a in dir(t))
    if type_str == 'module':
        # For module, we manage to get the corresponding 'module' type
        # but the type doesn't bring much information about its content.
        # A hacky way to do so is to assume that the exception was something
        # like 'module_name.attribute' so that we can actually find the module
        # based on the name. Eventually, we check that the found object is a
        # module indeed. This is not failproof but it brings a whole lot of
        # interesting suggestions and the (minimal) risk is to have invalid
        # suggestions.
        module_name = frame.f_code.co_names[0]
        objs = get_objects_in_frame(frame)
        mod = objs[module_name][0].obj
        if inspect.ismodule(mod):
            attributes = set(dir(mod))

    return itertools.chain(
        suggest_attribute_as_builtin(attribute, type_str, frame),
        suggest_attribute_alternative(attribute, type_str, attributes),
        suggest_attribute_synonyms(attribute, attributes),
        suggest_attribute_as_typo(attribute, attributes))


def suggest_attribute_as_builtin(attribute, type_str, frame):
    """Suggest that a builtin was used as an attribute.

    Example: 'lst.len()' -> 'len(lst)'.
    """
    if attribute in frame.f_builtins:
        yield quote(attribute + '(' + type_str + ')')


def suggest_attribute_alternative(attribute, type_str, attributes):
    """Suggest alternative to the non-found attribute."""
    is_iterable = '__iter__' in attributes or \
                  ('__getitem__' in attributes and '__len__' in attributes)
    if attribute == 'has_key' and '__contains__' in attributes:
        yield quote('key in ' + type_str) + ' (has_key is removed)'
    elif attribute == 'get' and '__getitem__' in attributes:
        yield quote('obj[key]') + \
            ' with a len() check or try: except: KeyError or IndexError'
    elif attribute in ('__setitem__', '__delitem__'):
        if is_iterable:
            msg = 'convert to list to edit the list'
            if 'join' in attributes:
                msg += ' and use "join()" on the list'
            yield msg
    elif attribute == '__getitem__':
        if '__call__' in attributes:
            yield quote(type_str + '(value)')
        if is_iterable:
            yield 'convert to list first or use the iterator protocol to ' \
                    'get the different elements'
    elif attribute == '__call__':
        if '__getitem__' in attributes:
            yield quote(type_str + '[value]')
    elif attribute == '__len__':
        if is_iterable:
            yield quote('len(list(' + type_str + '))')
    elif attribute == 'join':
        if is_iterable:
            yield quote('my_string.join(' + type_str + ')')


def suggest_attribute_synonyms(attribute, attributes):
    """Suggest that a method with a similar meaning was used.

    Example: 'lst.add(e)' -> 'lst.append(e)'.
    """
    for set_sub in SYNONYMS_SETS:
        if attribute in set_sub:
            for syn in set_sub & attributes:
                yield quote(syn)


def suggest_attribute_as_typo(attribute, attributes):
    """Suggest the attribute could be a typo.

    Example: 'a.do_baf()' -> 'a.do_bar()'.
    """
    for name in get_close_matches(attribute, attributes):
        # Handle Private name mangling
        if name.startswith('_') and '__' in name and not name.endswith('__'):
            yield quote(name) + ' (but it is supposed to be private)'
        else:
            yield quote(name)


# Functions related to ImportError
def suggest_imported_name_as_typo(imported_name, module_name, frame):
    """Suggest that imported name could be a typo from actual name in module.

    Example: 'from math import pie' -> 'from math import pi'.
    """
    dir_mod = dir(import_from_frame(module_name, frame))
    for name in get_close_matches(imported_name, dir_mod):
        yield quote(name)


def suggest_import_from_module(imported_name, frame):
    """Suggest than name could be found in a standard module.

    Example: 'from itertools import pi' -> 'from math import pi'.
    """
    for mod in STAND_MODULES:
        if imported_name in dir(import_from_frame(mod, frame)):
            yield quote('from {0} import {1}'.format(mod, imported_name))


# Functions related to TypeError
def suggest_feature_not_supported(attr, type_str, frame):
    """Get suggestion for unsupported feature."""
    # 'Object does not support <feature>' exceptions
    # can be somehow seen as attribute errors for magic
    # methods except for the fact that we do not want to
    # have any fuzzy logic on the magic method name.
    # Also, we want to suggest the implementation of the
    # missing method (it is it not on a builtin object).
    types = get_types_for_str(type_str, frame)
    attributes = set(a for t in types for a in dir(t))
    for s in suggest_attribute_alternative(attr, type_str, attributes):
        yield s
    if type_str not in frame.f_builtins and \
            type_str not in ('function', 'generator'):
        yield 'implement "' + attr + '" on ' + type_str


def get_func_by_name(func_name, frame):
    """Get the function with the given name in the frame."""
    objs = get_objects_in_frame(frame)
    # Trying to fetch reachable objects: getting objects and attributes
    # for objects. We would go deeper (with a fixed point algorithm) but
    # it doesn't seem to be worth it. In any case, we'll be missing a few
    # possible functions.
    objects = [o.obj for lst in objs.values() for o in lst]
    for obj in list(objects):
        for a in dir(obj):
            attr = getattr(obj, a, None)
            if attr is not None:
                objects.append(attr)
    # Then, we filter for function with the correct name (the name being the
    # name on the function object which is not always the same from the
    # namespace).
    return [func
            for func in objects
            if getattr(func, '__name__', None) == func_name]


def suggest_memory_friendly_equi(name, objs):
    """Suggest name of a memory friendly equivalent for a function."""
    suggs = {'range': ['xrange']}
    return [quote(s) for s in suggs.get(name, []) if s in objs]


def suggest_if_file_does_not_exist(value):
    """Get suggestions when a file does not exist."""
    # TODO: Add fuzzy match
    filename = value.filename
    for func, name in (
            (os.path.expanduser, 'os.path.expanduser'),
            (os.path.expandvars, 'os.path.expandvars')):
        expanded = func(filename)
        if os.path.exists(expanded) and filename != expanded:
            yield quote(expanded) + " (calling " + name + ")"


def suggest_if_file_is_not_dir(value):
    """Get suggestions when a file should have been a dir and is not."""
    filename = value.filename
    yield quote(os.path.dirname(filename)) + " (calling os.path.dirname)"


def suggest_if_file_is_dir(value):
    """Get suggestions when a file is a dir and should not."""
    filename = value.filename
    listdir = sorted(os.listdir(filename))
    if listdir:
        trunc_l = listdir[:MAX_NB_FILES]
        truncated = listdir != trunc_l
        filelist = [quote(f) for f in trunc_l] + (["etc"] if truncated else [])
        yield "any of the {0} files in directory ({1})".format(
            len(listdir), ", ".join(filelist))
    else:
        yield "to add content to {0} first".format(filename)


def get_suggestions_for_exception(value, traceback):
    """Get suggestions for an exception."""
    frame = get_last_frame(traceback)
    return itertools.chain.from_iterable(
            func(value, frame)
            for error_type, functions in SUGGESTION_FUNCTIONS.items()
            if isinstance(value, error_type)
            for func in functions)


def add_string_to_exception(value, string):
    """Add string to the exception parameter."""
    # The point is to have the string visible when the exception is printed
    # or converted to string - may it be via `str()`, `repr()` or when the
    # exception is uncaught and displayed (which seems to use `str()`).
    # In an ideal world, one just needs to update `args` but apparently it
    # is not enough for SyntaxError, IOError, etc where other
    # attributes (`msg`, `strerror`, `reason`, etc) are to be updated too
    # (for `str()`, not for `repr()`).
    # Also, elements in args might not be strings or args might me empty
    # so we add to the first string and add the element otherwise.
    assert type(value.args) == tuple
    if string:
        lst_args = list(value.args)
        for i, arg in enumerate(lst_args):
            if isinstance(arg, str):
                lst_args[i] = arg + string
                break
        else:
            # if no string arg, add the string anyway
            lst_args.append(string)
        value.args = tuple(lst_args)
        for attr in ['msg', 'strerror', 'reason']:
            attrval = getattr(value, attr, None)
            if attrval is not None:
                setattr(value, attr, attrval + string)


def get_last_frame(traceback):
    """Extract last frame from a traceback."""
    # In some rare case, the give traceback might be None
    if traceback is None:
        return None
    while traceback.tb_next:
        traceback = traceback.tb_next
    return traceback.tb_frame


def add_suggestions_to_exception(type_, value, traceback):
    """Add suggestion to an exception.

    Arguments are such as provided by sys.exc_info().
    """
    assert isinstance(value, type_)
    add_string_to_exception(
        value,
        get_suggestion_string(
            get_suggestions_for_exception(
                value,
                traceback)))
