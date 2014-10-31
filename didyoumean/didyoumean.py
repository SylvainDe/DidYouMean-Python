# -*- coding: utf-8
"""Logic to add suggestions to exceptions."""
import difflib
import re

#: Standard modules we'll consider while searching for undefined values
# To be completed
STAND_MODULES = set(['string', 'os', 'sys', 're', 'math', 'random',
                     'datetime', 'timeit', 'unittest', 'itertools',
                     'functools'])


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
    change default values or implementation defails easily."""
    return difflib.get_close_matches(word, possibilities)


def get_var_suggestions(var, frame):
    """Get the lim suggestions closest to the variable names."""
    sugg = []
    objs = get_objects_in_frame(frame)
    for name, obj in objs.items():
        if hasattr(obj, var):
            sugg.append(name + '.' + var)
    if var in STAND_MODULES:
        sugg.append('import ' + var)
    sugg.extend(get_close_matches(
        var,
        list(objs.keys())))
    return sugg


def get_method_suggestions(type_str, method, frame):
    """Get the lim suggestions closest to the method name for a given type."""
    sugg = []
    if method in frame.f_builtins:
        sugg.append(method + '(' + type_str + ')')
    # todo : add hardcoded logic for usual containers : add, append, etc
    if type_str != 'module':
        objs = get_objects_in_frame(frame)
        sugg.extend(get_close_matches(
            method,
            dir(objs[type_str])))
    return sugg


def get_suggestion_string(sugg):
    """Return the suggestion list as a string."""
    return ". Did you mean " + ', '.join(sugg) if sugg else ""


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
              frame.f_code.co_name)
        traceback = traceback.tb_next


def add_suggestions_to_exception(type_, value, traceback):
    """Add suggestion to an exception.
    Arguments are such as provided by sys.exc_info()."""
    # We care about the last element of the traceback
    end_traceback = traceback
    while end_traceback.tb_next:
        end_traceback = end_traceback.tb_next
    if issubclass(type_, NameError):
        assert len(value.args) == 1
        match = re.match("^(global )?name '(\w+)' is not defined$", value.args[0])
        assert match, "No match for %s" % value.args[0]
        _, var = match.groups()
        sugg = get_var_suggestions(var, end_traceback.tb_frame)
        value.args = (value.args[0] + get_suggestion_string(sugg), )
        assert len(value.args) == 1
    elif issubclass(type_, AttributeError):
        assert len(value.args) == 1
        match = re.match("^'(\w+)' object has no attribute '(\w+)'$", value.args[0])
        assert match, "No match for %s" % value.args[0]
        type_str, method = match.groups()
        sugg = get_method_suggestions(type_str, method, end_traceback.tb_frame)
        value.args = (value.args[0] + get_suggestion_string(sugg), )
        assert len(value.args) == 1
    elif issubclass(type_, TypeError):
        assert len(value.args) == 1
        match = re.match("^'(\w+)' object is not subscriptable$", value.args[0])
        if match:  # It could be cool to extract relevant info from the trace
            type_str, = match.groups()
            if type_str == 'function':
                value.args = (value.args[0] + get_suggestion_string([type_str + '(value)']), )
        assert len(value.args) == 1
    elif issubclass(type_, ImportError):
        assert len(value.args) == 1
        match = re.match("^No module named '?(\w+)'?$", value.args[0])
        if match:
            module_str, = match.groups()
            sugg = get_close_matches(module_str, STAND_MODULES)
            value.args = (value.args[0] + get_suggestion_string(sugg), )
        else:
            match = re.match("^cannot import name '?(\w+)'?$", value.args[0])
            assert match, "No match for %s" % value.args[0]
        assert len(value.args) == 1
    else:
        print(type_, value.args)
    # Could be added : IndexError, KeyError
