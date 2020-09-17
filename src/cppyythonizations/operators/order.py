r"""
Pythonizations to fill in missing operators <, <=, >, >=, ==, !=.

EXAMPLES::

   >>> import cppyy
   >>> from cppyythonizations.operators.order import enable_total_order
   >>> cppyy.py.add_pythonization(enable_total_order, "doctest::operators")

We define a C++ class with boost operators::

   >>> cppyy.include("boost/operators.hpp")
   True
   >>> cppyy.cppdef(r'''
   ... namespace doctest::operators {
   ...   struct TotallyOrdered : boost::totally_ordered<TotallyOrdered> {
   ...     bool operator<(const TotallyOrdered&) { return true; }
   ...     bool operator==(const TotallyOrdered&) { return true; }
   ...   };
   ... }''')
   True

Operators work on instances of this class::

    >>> demo = cppyy.gbl.doctest.operators.TotallyOrdered()
    >>> demo <= demo
    True

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
bool lt(T&& lhs, S&& rhs) { return std::forward<T>(lhs) < std::forward<S>(rhs); }
template <typename T, typename S>
bool gt(T&& lhs, S&& rhs) { return std::forward<T>(lhs) > std::forward<S>(rhs); }
template <typename T, typename S>
bool le(T&& lhs, S&& rhs) { return std::forward<T>(lhs) <= std::forward<S>(rhs); }
template <typename T, typename S>
bool ge(T&& lhs, S&& rhs) { return std::forward<T>(lhs) >= std::forward<S>(rhs); }
template <typename T, typename S>
bool eq(T&& lhs, S&& rhs) { return std::forward<T>(lhs) == std::forward<S>(rhs); }
template <typename T, typename S>
bool ne(T&& lhs, S&& rhs) { return std::forward<T>(lhs) != std::forward<S>(rhs); }
}
''')

def enable_total_order(proxy, name):
    r"""
    A `Pythonization <https://cppyy.readthedocs.io/en/latest/pythonizations.html>`
    to make sure that all comparison operators from C++ are actually picked up
    by cppyy.

    EXAMPLES::

        >>> import cppyy
        >>> from cppyythonizations.operators.order import enable_total_order
        >>> from cppyythonizations.util import filtered
        >>> cppyy.py.add_pythonization(filtered('__gmp_expr<__mpz_struct[1],__mpz_struct[1]>')(enable_total_order))
        >>> cppyy.include("gmpxx.h")
        True
        >>> cppyy.load_library("gmpxx")
        True
        >>> x = cppyy.gbl.mpz_class(0)
        >>> x < x
        False
        >>> x <= x
        True
        >>> x > x
        False
        >>> x >= x
        True
        >>> x == x
        True
        >>> x != x
        False

    """
    proxy.__lt__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.lt(self, rhs)
    proxy.__gt__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.gt(self, rhs)
    proxy.__le__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.le(self, rhs)
    proxy.__ge__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.ge(self, rhs)
    proxy.__ne__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.ne(self, rhs)
    proxy.__eq__ = lambda self, rhs: cppyy.gbl.cppyythonizations.operators.eq(self, rhs)
