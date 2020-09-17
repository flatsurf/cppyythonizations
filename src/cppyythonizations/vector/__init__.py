r"""
Modifies some aspects std::vector such as printing.

EXAMPLES::

    >>> import cppyy
    >>> from cppyythonizations.vector import add_vector_pythonizations
    >>> add_vector_pythonizations()
    >>> cppyy.gbl.std.vector[int]([1, 2, 3])
    [1, 2, 3]

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

import re
import cppyy

from ..util import filtered

def enable_list_printing(proxy, name):
    r"""
    Print proxy objects as lists.

    EXAMPLES::

        >>> import cppyy
        >>> from cppyythonizations.vector import enable_list_printing
        >>> from cppyythonizations.util import filtered
        >>> cppyy.py.add_pythonizations(filtered("set<int>")(enable_list_printing))
        >>> cppyy.gbl.std.set[int]()
        []

    """
    proxy.__repr__ = lambda self: repr(list(self))
    proxy.__str__ = lambda self: str(list(self))

def add_vector_pythonizations():
    r"""
    Enable printing of `std::vector<>` as a Python list.

    EXAMPLES::

        >>> import cppyy
        >>> from cppyythonizations.vector import add_vector_pythonizations
        >>> add_vector_pythonizations()
        >>> cppyy.gbl.std.vector[int]()
        []

    """
    cppyy.py.add_pythonization(filtered(re.compile("vector<.*>"))(enable_list_printing), "std")