r"""
Pythonizations to fill in missing operators arithmetic operators.

EXAMPLES::

   >>> import cppyy
   >>> from cppyythonizations.operators.arithmetic import enable_arithmetic
   >>> cppyy.py.add_pythonization(enable_arithmetic, "doctest::operators")

We define a C++ class with boost operators::

   >>> cppyy.include("boost/operators.hpp")
   >>> cppyy.cppdef(r'''
   ... namespace doctest::operators {
   ...   struct Addable : boost::addable<Addable> {
   ...     Addable& operator+=(const Addable&) { return *this; }
   ...   };
   ... }''')
   True

Operators work on instances of this class::

    >>> demo = cppyy.gbl.doctest.operators.Addable()
    >>> demo + demo
    <cppyy.gbl.doctest.operators.Addable ...>

"""
# ********************************************************************
#  This file is part of cppyythonizations.
#
#        Copyright (C) 2020 Julian Rüth
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ********************************************************************

import cppyy

cppyy.cppdef('''
namespace cppyythonizations::operators {
template <typename T, typename S>
auto add(T&& lhs, S&& rhs) { return std::forward<T>(lhs) + std::forward<S>(rhs); }
template <typename T, typename S>
auto sub(T&& lhs, S&& rhs) { return std::forward<T>(lhs) - std::forward<S>(rhs); }
template <typename T, typename S>
auto mul(T&& lhs, S&& rhs) { return std::forward<T>(lhs) * std::forward<S>(rhs); }
template <typename T, typename S>
auto truediv(T&& lhs, S&& rhs) { return std::forward<T>(lhs) / std::forward<S>(rhs); }
template <typename T, typename S>
auto mod(T&& lhs, S&& rhs) { return std::forward<T>(lhs) % std::forward<S>(rhs); }
template <typename T, typename S>
auto lshift(T&& lhs, S&& rhs) { return std::forward<T>(lhs) << std::forward<S>(rhs); }
template <typename T, typename S>
auto rshift(T&& lhs, S&& rhs) { return std::forward<T>(lhs) >> std::forward<S>(rhs); }

template <typename T, typename S>
auto radd(T&& rhs, S&& lhs) { return std::forward<T>(lhs) + std::forward<S>(rhs); }
template <typename T, typename S>
auto rsub(T&& rhs, S&& lhs) { return std::forward<T>(lhs) - std::forward<S>(rhs); }
template <typename T, typename S>
auto rmul(T&& rhs, S&& lhs) { return std::forward<T>(lhs) * std::forward<S>(rhs); }
template <typename T, typename S>
auto rtruediv(T&& rhs, S&& lhs) { return std::forward<T>(lhs) / std::forward<S>(rhs); }
template <typename T, typename S>
auto rmod(T&& rhs, S&& lhs) { return std::forward<T>(lhs) % std::forward<S>(rhs); }
template <typename T, typename S>
auto rlshift(T&& rhs, S&& lhs) { return std::forward<T>(lhs) << std::forward<S>(rhs); }
template <typename T, typename S>
auto rrshift(T&& rhs, S&& lhs) { return std::forward<T>(lhs) >> std::forward<S>(rhs); }

template <typename T, typename S>
T& iadd(T& lhs, S&& rhs) { return lhs += std::forward<S>(rhs); }
template <typename T, typename S>
T& isub(T& lhs, S&& rhs) { return lhs -= std::forward<S>(rhs); }
template <typename T, typename S>
T& imul(T& lhs, S&& rhs) { return lhs *= std::forward<S>(rhs); }
template <typename T, typename S>
T& itruediv(T& lhs, S&& rhs) { return lhs /= std::forward<S>(rhs); }
template <typename T, typename S>
T& imod(T& lhs, S&& rhs) { return lhs %= std::forward<S>(rhs); }
template <typename T, typename S>
T& ilshift(T& lhs, S&& rhs) { return lhs <<= std::forward<S>(rhs); }
template <typename T, typename S>
T& irshift(T& lhs, S&& rhs) { return lhs >>= std::forward<S>(rhs); }
}

''')

def enable_arithmetic(proxy, name):
    r"""
    A `Pythonization <https://cppyy.readthedocs.io/en/latest/pythonizations.html>`
    to make sure that all arithmetic operators from C++ are actually picked up
    by cppyy.

    """
    enable_addable(proxy, name)
    enable_subtractable(proxy, name)
    enable_multipliable(proxy, name)
    enable_dividable(proxy, name)

def enable_addable(proxy, name):
    proxy.__add__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.add(self, rhs)
    proxy.__iadd__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.iadd(self, rhs)
    proxy.__radd__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.radd(self, rhs)

def enable_subtractable(proxy, name):
    proxy.__sub__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.sub(self, rhs)
    proxy.__isub__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.isub(self, rhs)
    proxy.__rsub__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.rsub(self, rhs)

def enable_multipliable(proxy, name):
    proxy.__mul__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.mul(self, rhs)
    proxy.__imul__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.imul(self, rhs)
    proxy.__rmul__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.rmul(self, rhs)

def enable_dividable(proxy, name):
    proxy.__truediv__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.truediv(self, rhs)
    proxy.__itruediv__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.itruediv(self, rhs)
    proxy.__rtruediv__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.rtruediv(self, rhs)

def enable_modable(proxy, name):
    proxy.__mod__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.mod(self, rhs)
    proxy.__imod__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.imod(self, rhs)
    proxy.__rmod__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.rmod(self, rhs)

def enable_left_shiftable(proxy, name):
    proxy.__lshift__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.lshift(self, rhs)
    proxy.__ilshift__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.ilshift(self, rhs)

def enable_right_shiftable(proxy, name):
    proxy.__rshift__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.rshift(self, rhs)
    proxy.__irshift__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.irshift(self, rhs)

def enable_shiftable(proxy, name):
    enable_left_shiftable(proxy, name)
    enable_right_shiftable(proxy, name)
