r"""
Pythonizations to improve printing of types in cppyy.

EXAMPLES::

    >>> import cppyy
    >>> cppyy.cppdef("namespace demo { class X{}; }")
    True
    >>> cppyy.cppdef('std::ostream& operator<<(std::ostream& os, const demo::X&) { return os << "X()"; }')
    True

    >>> from cppyythonizations.printing import enable_pretty_printing
    >>> cppyy.py.add_pythonization(enable_pretty_printing, "demo")
    >>> cppyy.gbl.demo.X()
    X()

TESTS:

Modifying `__str__` changes how an element displays::

    >>> cppyy.gbl.demo.X.__str__ = lambda self: "Y()"
    >>> cppyy.gbl.demo.X()
    Y()

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

from ..vector import enable_list_printing

def enable_pretty_printing(proxy, name):
    proxy.__repr__ = lambda self: proxy.__str__(self)
