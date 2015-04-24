# -*- coding: utf-8
"""Code to generate examples in README.md."""
from didyoumean import add_suggestions_to_exception
import sys


def get_exception(code):
    """Helper function to run code and get what it throws."""
    try:
        exec(code)
    except:
        return sys.exc_info()
    assert False


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
                "def my_func(lst):\n\treturn leng(foo)\nmy_func([0])",
                "import math\nmaths.pi",
                "def my_func():\n\tpasss\nmy_func()",
                "def my_func():\n\tfoo = 1\n\tfoob +=1\nmy_func()"
            ],
            (2, "Checking if name is the attribute of a defined object"): [
                "class Duck():\n\tdef __init__(self):\n\t\tquack()"
                "\n\tdef quack(self):\n\t\tpass\nd = Duck()",
                "import math\npi",
            ],
            (3, "Looking for missing imports"): [
                "functools.wraps()",
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
        },
        (5, SyntaxError): {
            (1, "Fuzzy matches when importing from __future__"): [
                "from __future__ import divisio",
            ],
            (2, "Various"): [
                "return",
            ],
        },
        (6, MemoryError): {
            (1, "Search for a memory-efficient equivalent"): [
                # FIXME : This example will no work on all versions :
                # "range(99999999999)",
            ],
        },
    }

    str_func = repr  # could be str or repr
    for (_, exc_type), exc_examples in sorted(examples.items()):
        print("### %s\n" % exc_type.__name__)
        for (_, desc), codes in sorted(exc_examples.items()):
            print("##### %s\n" % desc)
            for code in codes:
                type_, value, traceback = get_exception(code)
                assert issubclass(type_, exc_type)
                before = str_func(value)
                add_suggestions_to_exception(type_, value, traceback)
                after = str_func(value)
                assert before != after
                print("""```python
%s
#>>> Before: %s
#>>> After: %s
```""" % (code, before, after))

if __name__ == '__main__':
    main()
