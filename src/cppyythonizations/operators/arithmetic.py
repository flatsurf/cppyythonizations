r"""
Pythonizations to fill in missing arithmetic operators

EXAMPLES::

   >>> import cppyy
   >>> from cppyythonizations.operators.arithmetic import enable_arithmetic
   >>> cppyy.py.add_pythonization(enable_arithmetic, "doctest::operators")

We define a C++ class with boost operators::

   >>> cppyy.include("boost/operators.hpp")
   True
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
template <typename T>
auto neg(const T& self) { return -self; }

template <typename T, typename S>
auto add(const T& lhs, const S& rhs) { return (lhs) + (rhs); }
template <typename T, typename S>
auto sub(const T& lhs, const S& rhs) { return (lhs) - (rhs); }
template <typename T, typename S>
auto mul(const T& lhs, const S& rhs) { return (lhs) * (rhs); }
template <typename T, typename S>
auto truediv(const T& lhs, const S& rhs) { return (lhs) / (rhs); }
template <typename T, typename S>
auto mod(const T& lhs, const S& rhs) { return (lhs) % (rhs); }
template <typename T, typename S>
auto lshift(const T& lhs, const S& rhs) { return (lhs) << (rhs); }
template <typename T, typename S>
auto rshift(const T& lhs, const S& rhs) { return (lhs) >> (rhs); }

template <typename S, typename T>
auto radd(const S& rhs, const T& lhs) { return (lhs) + (rhs); }
template <typename S, typename T>
auto rsub(const S& rhs, const T& lhs) { return (lhs) - (rhs); }
template <typename S, typename T>
auto rmul(const S& rhs, const T& lhs) { return (lhs) * (rhs); }
template <typename S, typename T>
auto rtruediv(const S& rhs, const T& lhs) { return (lhs) / (rhs); }
template <typename S, typename T>
auto rmod(const S& rhs, const T& lhs) { return (lhs) % (rhs); }
template <typename S, typename T>
auto rlshift(const S& rhs, const T& lhs) { return (lhs) << (rhs); }
template <typename S, typename T>
auto rrshift(const S& rhs, const T& lhs) { return (lhs) >> (rhs); }

template <typename T, typename S>
T& iadd(T& lhs, const S& rhs) { return lhs += std::forward<S>(rhs); }
template <typename T, typename S>
T& isub(T& lhs, const S& rhs) { return lhs -= std::forward<S>(rhs); }
template <typename T, typename S>
T& imul(T& lhs, const S& rhs) { return lhs *= std::forward<S>(rhs); }
template <typename T, typename S>
T& itruediv(T& lhs, const S& rhs) { return lhs /= std::forward<S>(rhs); }
template <typename T, typename S>
T& imod(T& lhs, const S& rhs) { return lhs %= std::forward<S>(rhs); }
template <typename T, typename S>
T& ilshift(T& lhs, const S& rhs) { return lhs <<= std::forward<S>(rhs); }
template <typename T, typename S>
T& irshift(T& lhs, const S& rhs) { return lhs >>= std::forward<S>(rhs); }
}

''')

def enable_operator(op, prefixes=["", "r", "i"]):
    def enable_operator_op(proxy, name, unwrap=None):
        namespace = cppyy.gbl.cppyythonizations.operators
        for prefix in prefixes:
            cpp_binary = getattr(namespace, prefix + op)
            def make_py_binary(cpp_binary):
                py_binary = lambda self, rhs: cpp_binary[type(self), type(rhs)](self, rhs)
                return py_binary if unwrap is None else lambda self, rhs: unwrap(py_binary(self, rhs))
            setattr(proxy, "__" + prefix + op + "__", make_py_binary(cpp_binary))
    return enable_operator_op

def enable_neg(proxy, name, unwrap=None):
    enable_operator("neg", [""])(proxy, name, unwrap)

def enable_addable(proxy, name, unwrap=None):
    enable_operator("add")(proxy, name, unwrap)

def enable_subtractable(proxy, name, unwrap=None):
    enable_operator("sub")(proxy, name, unwrap)

def enable_multipliable(proxy, name, unwrap=None):
    enable_operator("mul")(proxy, name, unwrap)

def enable_dividable(proxy, name, unwrap=None):
    enable_operator("truediv")(proxy, name, unwrap)

def enable_modable(proxy, name, unwrap=None):
    enable_operator("mod")(proxy, name, unwrap)

def enable_left_shiftable(proxy, name, unwrap=None):
    enable_operator("lshift")(proxy, name, unwrap)

def enable_right_shiftable(proxy, name, unwrap=None):
    enable_operator("rshift")(proxy, name, unwrap)

def enable_arithmetic(proxy, name, unwrap=None):
    r"""
    A `Pythonization <https://cppyy.readthedocs.io/en/latest/pythonizations.html>`
    to make sure that all arithmetic operators from C++ are actually picked up
    by cppyy.

    """
    enable_addable(proxy, name, unwrap)
    enable_subtractable(proxy, name, unwrap)
    enable_multipliable(proxy, name, unwrap)
    enable_dividable(proxy, name, unwrap)

def enable_shiftable(proxy, name, unwrap=None):
    enable_left_shiftable(proxy, name, unwrap)
    enable_right_shiftable(proxy, name, unwrap)
