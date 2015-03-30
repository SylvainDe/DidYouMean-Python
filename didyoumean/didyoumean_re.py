# -*- coding: utf-8
"""Regular expressions to parse error messages."""

UNBOUNDERROR_RE = r"^local variable '(\w+)' referenced before assignment$"
NAMENOTDEFINED_RE = r"^(?:global )?name '(\w+)' is not defined$"
ATTRIBUTEERROR_RE = r"^'?([\w\.]+)'? (?:object|instance) " \
    "has no attribute '(\w+)'$"
UNSUBSCRIBTABLE_RE = r"^'(\w+)' object " \
    "(?:is (?:not |un)subscriptable|has no attribute '__getitem__')$"
UNEXPECTED_KEYWORDARG_RE = r"^(\w+)\(\) " \
    "got an unexpected keyword argument '(\w+)'$"
NOMODULE_RE = r"^No module named '?(\w+)'?$"
CANNOTIMPORT_RE = r"^cannot import name '?(\w+)'?$"
INDEXOUTOFRANGE_RE = r"^list index out of range$"
