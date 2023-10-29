# -*- coding: utf-8
"""Code to generate examples in README.md."""
from didyoumean_internal import add_suggestions_to_exception
import didyoumean_common_tests as common
import datetime
import os
import sys
import traceback
from test.support import captured_stderr
import io
import contextlib


def standardise(string):
    """Standardise string by removing elements from the environment.

    Replace strings from the environment by the name of the environment
    variable.
    """
    for var in ["USER"]:
        val = os.environ.get(var)
        if val is not None:
            string = string.replace(val, var.lower())
    return string


# Functions to try to get the string representation for an exception


def get_except_hook_result_as_str(type_, value, traceback):
    # Inspired from "get_message_lines" in Lib/idlelib/run.py
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        sys.__excepthook__(type_, value, traceback)
    return err.getvalue().split("\n")[-2]


def get_print_exception_result_as_str(value):
    # Trying with traceback
    with captured_stderr() as output:
        traceback.print_exception(value)
    return output.getvalue().splitlines()[-1]


def exception_to_str(type_, value, traceback):
    # Could be str(value), repr(value), get_print_exception_result_as_str(value) or get_except_hook_result_as_str
    return str(value)


# Different examples :
# Code examples are grouped by error type then by suggestion type
# Numbers have been added in dict keys just to be able to iterate
# over them and have the result in the wanted order.
EXAMPLES = {
    (1, NameError): {
        (
            1,
            "Fuzzy matches on existing names "
            "(local, builtin, keywords, modules, etc)",
        ): [
            "def my_func(foo, bar):\n\treturn foob\n\nmy_func(1, 2)",
            "leng([0])",
            "import math\nmaths.pi",
            "passs",
            "def my_func():\n\tfoo = 1\n\tfoob +=1\n\nmy_func()",
        ],
        (2, "Checking if name is the attribute of a defined object"): [
            "class Duck():\n\tdef __init__(self):\n\t\tquack()"
            "\n\tdef quack(self):\n\t\tpass\nd = Duck()",
            "import math\npi",
        ],
        (3, "Looking for missing imports"): [
            "string.ascii_lowercase",
        ],
        (4, "Looking in missing imports"): [
            "choice",
        ],
        (5, "Special cases"): [
            "assert j ** 2 == -1",
        ],
    },
    (2, AttributeError): {
        (1, "Fuzzy matches on existing attributes"): [
            "lst = [1, 2, 3]\nlst.appendh(4)",
            "import math\nmath.pie",
        ],
        (2, "Trying to find method with similar meaning (hardcoded)"): [
            "lst = [1, 2, 3]\nlst.add(4)",
            "lst = [1, 2, 3]\nlst.get(5, None)",
        ],
        (3, "Detection of mis-used builtins"): [
            "lst = [1, 2, 3]\nlst.max()",
        ],
        (4, "Period used instead of comma"): [
            "a, b = 1, 2\nmax(a. b)",
        ],
    },
    (3, ImportError): {
        (1, "Fuzzy matches on existing modules"): [
            "from maths import pi",
        ],
        (2, "Fuzzy matches on elements of the module"): [
            "from math import pie",
        ],
        (3, "Looking for import from wrong module"): [
            "from itertools import pi",
        ],
    },
    (4, TypeError): {
        (1, "Fuzzy matches on keyword arguments"): [
            "def my_func(abcde):\n\tpass\n\nmy_func(abcdf=1)",
        ],
        (2, "Confusion between brackets and parenthesis"): [
            "lst = [1, 2, 3]\nlst(0)",
            "def my_func(a):\n\tpass\n\nmy_func[1]",
        ],
    },
    (5, ValueError): {
        (1, "Special cases"): [
            "'Foo{}'.format('bar')",
            "import datetime\n" 'datetime.datetime.strptime("%d %b %y", "30 Nov 00")',
        ],
    },
    (6, SyntaxError): {
        (1, "Fuzzy matches when importing from __future__"): [
            "from __future__ import divisio",
        ],
        (2, "Various"): [
            "return",
        ],
    },
    (7, MemoryError): {
        (1, "Search for a memory-efficient equivalent"): [
            "range(999999999999999)",
        ],
    },
    (8, OverflowError): {
        (1, "Search for a memory-efficient equivalent"): [
            "range(999999999999999)",
        ],
    },
    (9, (OSError, IOError)): {
        (1, "Suggestion for tilde/variable expansions"): [
            "import os\nos.listdir('~')",
        ]
    },
    (10, RuntimeError): {
        (1, "Suggestion to avoid reaching maximum recursion depth"): [
            "global rec\ndef rec(n): return rec(n-1)\nrec(0)"
        ],
    },
}


def get_code_with_exc_before_and_after(code, exc_types):
    exc = common.get_exception(code)
    if exc is None:
        before = after = "No exception thrown on this version of Python"
    else:
        type_, value, traceback = exc
        if not issubclass(type_, exc_types):
            msg = "Wrong exception thrown on this version of Python (%s != %s)" % (
                type_,
                exc_types,
            )
            before = after = msg
        else:
            before = exception_to_str(type_, value, traceback)
            add_suggestions_to_exception(type_, value, traceback)
            after = exception_to_str(type_, value, traceback)
            if before == after:
                after += " (unchanged on this version of Python)"
    return """```python
{0}
#>>> Before: {1}
#>>> After: {2}
```""".format(
        code, before, after
    )


def main():
    """Main."""
    print(datetime.datetime.now())
    print(sys.version)
    for (_, exc_types), exc_examples in sorted(EXAMPLES.items()):
        if not isinstance(exc_types, tuple):
            exc_types = (exc_types,)
        print("### {0}\n".format("/".join(e.__name__ for e in exc_types)))
        for (_, desc), codes in sorted(exc_examples.items()):
            print("##### {0}\n".format(desc))
            for code in codes:
                print(standardise(get_code_with_exc_before_and_after(code, exc_types)))


if __name__ == "__main__":
    main()
