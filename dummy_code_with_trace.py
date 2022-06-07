def endlessly_recursive_func(n):
    """Call itself recursively with no end."""
    # http://stackoverflow.com/questions/871887/using-exec-with-recursive-functions
    return endlessly_recursive_func(n - 1)

def trace(frame, event, arg):
    return trace

import sys
sys.settrace(trace)

endlessly_recursive_func(0)
