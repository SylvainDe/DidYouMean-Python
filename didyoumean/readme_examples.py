# -*- coding: utf-8
"""Code to generate examples in README.md."""
from didyoumean_internal import add_suggestions_to_exception
import didyoumean_common_tests as common
import os


def standardise(string):
    """Standardise string by removing elements from the environment.

    Replace strings from the environment by the name of the environment
    variable.
    """
    for var in ['USER']:
        val = os.environ.get(var)
        if val is not None:
            string = string.replace(val, var.lower())
    return string


def main():
    """Main."""
    # Different examples :
    # Code examples are groupes by error type then by suggestion type
    # Numbers have been added in dict keys just to be able to iterate
    # over them and have the result in the wanted order.
    examples = {
        (1, NameError): {
            (1, "Fuzzy matches on existing names "
                "(local, builtin, keywords, modules, etc)"): [
                "def my_func(foo, bar):\n\treturn foob\nmy_func(1, 2)",
                "leng([0])",
                "import math\nmaths.pi",
                "passs",
                "def my_func():\n\tfoo = 1\n\tfoob +=1\nmy_func()"
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
            (2, "Detection of mis-used builtins"): [
                "lst = [1, 2, 3]\nlst.max()",
            ],
            (3, "Trying to find method with similar meaning (hardcoded)"): [
                "lst = [1, 2, 3]\nlst.add(4)",
                "lst = [1, 2, 3]\nlst.get(5, None)",
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
                "def my_func(abcde):\n\tpass\nmy_func(abcdf=1)",
            ],
            (2, "Confusion between brackets and parenthesis"): [
                "lst = [1, 2, 3]\nlst(0)",
                "def my_func(a):\n\tpass\nmy_func[1]",
            ],
        },
        (5, ValueError): {
            (1, "Special cases"): [
                "'Foo{}'.format('bar')",
                'import datetime\n'
                'datetime.datetime.strptime("%d %b %y", "30 Nov 00")',
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
                "os.listdir('~')",
            ]
        },
        (10, RuntimeError): {
            (1, "Suggestion to avoid reaching maximum recursion depth"): [
                "global rec\ndef rec(n): return rec(n-1)\nrec(0)"
            ],
        },
    }

    str_func = repr  # could be str or repr
    for (_, exc_types), exc_examples in sorted(examples.items()):
        if not isinstance(exc_types, tuple):
            exc_types = (exc_types, )
        print("### {0}\n".format("/".join(e.__name__ for e in exc_types)))
        for (_, desc), codes in sorted(exc_examples.items()):
            print("##### {0}\n".format(desc))
            for code in codes:
                exc = common.get_exception(code)
                if exc is None:
                    before = after = \
                        "No exception thrown on this version of Python"
                else:
                    type_, value, traceback = exc
                    if not issubclass(type_, exc_types):
                        before = after = \
                            "Wrong exception thrown on this version of Python"
                    else:
                        before = standardise(str_func(value))
                        add_suggestions_to_exception(type_, value, traceback)
                        after = standardise(str_func(value))
                        if before == after:
                            after += " (unchanged on this version of Python)"
                print("""```python
{0}
#>>> Before: {1}
#>>> After: {2}
```""".format(standardise(code), before, after))

if __name__ == '__main__':
    main()
