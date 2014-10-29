DidYouMean-Python
=================

[![Build Status](https://travis-ci.org/SylvainDe/DidYouMean-Python.svg)](https://travis-ci.org/SylvainDe/DidYouMean-Python)

Logic to have various kind of suggestions in case of errors (NameError, AttributeError, etc). Can be used via a simple import or a dedicated decorator.

Inspired by "Did you mean" for Ruby ([Explanation](http://www.yukinishijima.net/2014/10/21/did-you-mean-experience-in-ruby.html), [Github Page](https://github.com/yuki24/did_you_mean)), this is a simple implementation for/in Python. I wanted to see if I could mess around and create something similar in Python and it seems to be possible.


See also :

 - [PEP 473 :  Adding structured data to built-in exceptions](http://legacy.python.org/dev/peps/pep-0473/).

 - [dutc/didyoumean](https://github.com/dutc/didyoumean) : a quite similar project developed in pretty much the same time. A few differences though : written in C, works only for AttributeError, etc.



Example
-------

### Name Error

```python
def my_func(foo, bar):
    return foob

#>>> NameError: global name 'foob' is not defined

@didyoumean
def my_func2(foo, bar):
    return foob

#>>> NameError: global name 'foob' is not defined. Did you mean foo
```

### Attribute Error

```python
def my_func():
    lst = [1, 2, 3]
    lst.len()

#>>> AttributeError: 'list' object has no attribute 'len'

@didyoumean
def my_func2(foo, bar):
    lst = [1, 2, 3]
    lst.len()


#>>> AttributeError: 'list' object has no attribute 'len'. Did you mean len(list)
```

Usage
-----

I haven't done anything fancy for the installation (yet). You'll have to clone this.

Once you have the code, it can be used in two different ways :

 * hook on `sys.excepthook` : just `import didyoumean_hook` and you'll have the suggestions for any exception happening

 * decorator : just `import didyoumean_decorator` and add the `@didyoumean` decorator before any function (the `main()` could be a good choice) and you'll have the suggestions for any exception happening through a call to that method.


Implementation
--------------

Both the hook and the decorator use the same logic behind the scene. It works in a pretty simple way : when an exception happens, we try to get the relevant information out of the error message and of the backtrace to find the most relevant suggestions. To filter the best suggestions out of everything, I am currently using ```difflib```.


Contributing
------------

Feedback is welcome, feel free to :
 * send me an email for any question/advice/comment/criticism
 * open issues if something goes wrong (please provide at least the version of Python you are using).

Also, pull-requests are welcome to :
 * fix issues
 * enhance the documentation
 * improve the code
 * bring awesomeness

As for the technical details :

 * this is under MIT License : you can do anything you want as long as you provide attribution back to this project.
 * I try to follow [PEP 8](http://legacy.python.org/dev/peps/pep-0008/) as much as possible
 * I try to have most of the code covered by unit tests
