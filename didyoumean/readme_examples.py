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
    examples = {
        NameError: {
            "Fuzzy matches on existing names "
            "(local, builtin, keywords, modules, etc)": [
                "def my_func(foo, bar):\n\treturn foob\nmy_func(1, 2)",
                "def my_func(lst):\n\treturn leng(foo)\nmy_func([0])",
                "import math\nmaths.pi",
                "def my_func():\n\tpasss\nmy_func()",
                "def my_func():\n\tfoo = 1\n\tfoob +=1\nmy_func()"
            ],
            "Checking if name is the attribute of a defined object": [
                "class Duck():\n\tdef __init__(self):\n\t\tquack()"
                "\n\tdef quack(self):\n\t\tpass\nd = Duck()",
                "import math\npi",
            ],
            "Looking for missing imports": [
                "functools.wraps()",
            ],
        },
        AttributeError: {
            "Fuzzy matches on existing attributes": [
                "lst = [1, 2, 3]\nlst.appendh(4)",
                "import math\nmath.pie",
            ],
            "Detection of mis-used builtins": [
                "lst = [1, 2, 3]\nlst.max()",
            ],
            "Trying to find method with similar meaning (hardcoded)": [
                "lst = [1, 2, 3]\nlst.add(4)",
            ],
        },
        ImportError: {
            "Fuzzy matches on existing modules": [
                "from maths import pi",
            ],
            "Fuzzy matches on elements of the module": [
                "from math import pie",
            ],
        },
        TypeError: {
            "Fuzzy matches on keyword arguments": [
                "def my_func(abcde):\n\tpass\nmy_func(abcdf=1)",
            ],
        },
        SyntaxError: {
            "Various": [
                "return",
            ],
            "Fuzzy matches when importing from __future__": [
                "from __future__ import divisio",
            ]
        },
    }

    str_func = repr  # could be str or repr
    for exc_type, exc_examples in examples.items():
        print("### %s\n" % exc_type.__name__)
        for desc, codes in exc_examples.items():
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
