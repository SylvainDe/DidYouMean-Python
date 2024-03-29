Tests performed with a recent version of Python to check which errors leads to which type of suggestion.

Unfortunately, the implemented suggestions are not easy to retrieve programmatically as they are only computed and added when the error is uncaught and displayed to the user.

The logic happens from the following places:
 - Python/pythonrun.c:1212:print_exception(struct exception_print_context *ctx, PyObject *value)
 - Python/pythonrun.c:1104:print_exception_suggestions(struct exception_print_context *ctx, ...)
 - Python/suggestions.c:269:_Py_Offer_Suggestions(PyObject *exception)

Using some inspiration from Lib/idlelib/idle_test/test_run.py , a workaround was found.

Here is the corresponding output with Python 3.11.0b3 (main, Jun  1 2022, 23:51:17) [GCC 9.4.0].

3.11.0b3 (main, Jun  1 2022, 23:51:17) [GCC 9.4.0]
### NameError

##### Fuzzy matches on existing names (local, builtin, keywords, modules, etc)

```python
def my_func(foo, bar):
	return foob

my_func(1, 2)
#>>> Before: NameError: name 'foob' is not defined. Did you mean: 'foo'?
#>>> After: NameError: name 'foob' is not defined. Did you mean 'foo' (local)?. Did you mean: 'foo'?
# My comment: the suggestion looks good! (My suggestion is not relevant anymore now)
```
```python
leng([0])
#>>> Before: NameError: name 'leng' is not defined. Did you mean: 'len'?
#>>> After: NameError: name 'leng' is not defined. Did you mean 'len' (builtin)?. Did you mean: 'len'?
# My comment: the suggestion looks good! (My suggestion is not relevant anymore now)
```
```python
import math
maths.pi
#>>> Before: NameError: name 'maths' is not defined
#>>> After: NameError: name 'maths' is not defined. Did you mean 'math' (local)?
# My comment: the suggestion looks good! (My suggestion is not relevant anymore now)
```
```python
passs
#>>> Before: NameError: name 'passs' is not defined
#>>> After: NameError: name 'passs' is not defined. Did you mean 'pass' (keyword)?
# My comment: the suggestion could include keywords
```
```python
def my_func():
	foo = 1
	foob +=1

my_func()
#>>> Before: UnboundLocalError: cannot access local variable 'foob' where it is not associated with a value
#>>> After: UnboundLocalError: cannot access local variable 'foob' where it is not associated with a value. Did you mean 'foo' (local)?
# My comment: the suggestion could be added for UnboundLocalError
```
##### Checking if name is the attribute of a defined object

```python
class Duck():
	def __init__(self):
		quack()
	def quack(self):
		pass
d = Duck()
#>>> Before: NameError: name 'quack' is not defined
#>>> After: NameError: name 'quack' is not defined. Did you mean 'self.quack'?
# My comment: the suggestion looks okay but we can do better!
```
```python
import math
pi
#>>> Before: NameError: name 'pi' is not defined
#>>> After: NameError: name 'pi' is not defined. Did you mean 'math.pi'?
```
##### Looking for missing imports

```python
string.ascii_lowercase
#>>> Before: NameError: name 'string' is not defined
#>>> After: NameError: name 'string' is not defined. Did you mean to import string first?
```
##### Looking in missing imports

```python
choice
#>>> Before: NameError: name 'choice' is not defined
#>>> After: NameError: name 'choice' is not defined. Did you mean 'choice' from random (not imported)?
```
##### Special cases

```python
assert j ** 2 == -1
#>>> Before: NameError: name 'j' is not defined
#>>> After: NameError: name 'j' is not defined. Did you mean '1j' (imaginary unit)?
```
### AttributeError

##### Fuzzy matches on existing attributes

```python
lst = [1, 2, 3]
lst.appendh(4)
#>>> Before: AttributeError: 'list' object has no attribute 'appendh'. Did you mean: 'append'?
#>>> After: AttributeError: 'list' object has no attribute 'appendh'. Did you mean 'append'?. Did you mean: 'append'?
# My comment: the suggestion looks good! (My suggestion is not relevant anymore now)
```
```python
import math
math.pie
#>>> Before: AttributeError: module 'math' has no attribute 'pie'. Did you mean: 'pi'?
#>>> After: AttributeError: module 'math' has no attribute 'pie'. Did you mean 'pi'?. Did you mean: 'pi'?
# My comment: the suggestion looks good! (My suggestion is not relevant anymore now)
```
##### Trying to find method with similar meaning (hardcoded)

```python
lst = [1, 2, 3]
lst.add(4)
#>>> Before: AttributeError: 'list' object has no attribute 'add'
#>>> After: AttributeError: 'list' object has no attribute 'add'. Did you mean 'append'?
```
```python
lst = [1, 2, 3]
lst.get(5, None)
#>>> Before: AttributeError: 'list' object has no attribute 'get'
#>>> After: AttributeError: 'list' object has no attribute 'get'. Did you mean 'obj[key]' with a len() check or try: except: KeyError or IndexError?
```
##### Detection of mis-used builtins

```python
lst = [1, 2, 3]
lst.max()
#>>> Before: AttributeError: 'list' object has no attribute 'max'
#>>> After: AttributeError: 'list' object has no attribute 'max'. Did you mean 'max(list)'?
```
##### Period used instead of comma

```python
a, b = 1, 2
max(a. b)
#>>> Before: AttributeError: 'int' object has no attribute 'b'
#>>> After: AttributeError: 'int' object has no attribute 'b'. Did you mean to use a comma instead of a period?
```
### ImportError

##### Fuzzy matches on existing modules

```python
from maths import pi
#>>> Before: ModuleNotFoundError: No module named 'maths'
#>>> After: ModuleNotFoundError: No module named 'maths'. Did you mean 'math'?
```
##### Fuzzy matches on elements of the module

```python
from math import pie
#>>> Before: ImportError: cannot import name 'pie' from 'math' (unknown location)
#>>> After: ImportError: cannot import name 'pie' from 'math' (unknown location). Did you mean 'pi'?
```
##### Looking for import from wrong module

```python
from itertools import pi
#>>> Before: ImportError: cannot import name 'pi' from 'itertools' (unknown location)
#>>> After: ImportError: cannot import name 'pi' from 'itertools' (unknown location). Did you mean 'from math import pi'?
```
### TypeError

##### Fuzzy matches on keyword arguments

```python
def my_func(abcde):
	pass

my_func(abcdf=1)
#>>> Before: TypeError: my_func() got an unexpected keyword argument 'abcdf'
#>>> After: TypeError: my_func() got an unexpected keyword argument 'abcdf'. Did you mean 'abcde'?
```
##### Confusion between brackets and parenthesis

```python
lst = [1, 2, 3]
lst(0)
#>>> Before: TypeError: 'list' object is not callable
#>>> After: TypeError: 'list' object is not callable. Did you mean 'list[value]'?
```
```python
def my_func(a):
	pass

my_func[1]
#>>> Before: TypeError: 'function' object is not subscriptable
#>>> After: TypeError: 'function' object is not subscriptable. Did you mean 'function(value)'?
```
### ValueError

##### Special cases

```python
'Foo{}'.format('bar')
#>>> Before: No exception thrown on this version of Python
#>>> After: No exception thrown on this version of Python
```
```python
import datetime
datetime.datetime.strptime("%d %b %y", "30 Nov 00")
#>>> Before: ValueError: time data '%d %b %y' does not match format '30 Nov 00'
#>>> After: ValueError: time data '%d %b %y' does not match format '30 Nov 00'. Did you mean to swap value and format parameters?
```
### SyntaxError

##### Fuzzy matches when importing from __future__

```python
from __future__ import divisio
#>>> Before: SyntaxError: future feature divisio is not defined
#>>> After: SyntaxError: future feature divisio is not defined. Did you mean 'division'?
```
##### Various

```python
return
#>>> Before: SyntaxError: 'return' outside function
#>>> After: SyntaxError: 'return' outside function. Did you mean to indent it, 'sys.exit([arg])'?
```
### MemoryError

##### Search for a memory-efficient equivalent

```python
range(999999999999999)
#>>> Before: No exception thrown on this version of Python
#>>> After: No exception thrown on this version of Python
```
### OverflowError

##### Search for a memory-efficient equivalent

```python
range(999999999999999)
#>>> Before: No exception thrown on this version of Python
#>>> After: No exception thrown on this version of Python
```
### OSError/OSError

##### Suggestion for tilde/variable expansions

```python
import os
os.listdir('~')
#>>> Before: FileNotFoundError: [Errno 2] No such file or directory: '~'
#>>> After: FileNotFoundError: [Errno 2] No such file or directory. Did you mean '/home/user' (calling os.path.expanduser)?: '~'
```
### RuntimeError

##### Suggestion to avoid reaching maximum recursion depth

```python
global rec
def rec(n): return rec(n-1)
rec(0)
#>>> Before: RecursionError: maximum recursion depth exceeded
#>>> After: RecursionError: maximum recursion depth exceeded. Did you mean to avoid recursion (cf http://neopythonic.blogspot.fr/2009/04/tail-recursion-elimination.html), increase the limit with `sys.setrecursionlimit(limit)` (current value is 1000)?
```
