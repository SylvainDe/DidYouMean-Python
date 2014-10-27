# -*- coding: utf-8
"""Unit tests for code in didyoumean.py."""

from didyoumean import didyoumean
# import unittest


def func(a, b):
    print("func")
    c = 5
    f = []
    f.add(c)
    # c = [5 for i in range(10) if b2 > 0]
    c = b2
    e = {}
    e[3] = 3
    # c = e[2 + 5]


def func2():
    print("func2")
    fun = 2
    func(1, 2)


@didyoumean
def func3():
    print("func3")
    func2()


func3()
