r"""
Modifies some aspects std::vector such as printing.

EXAMPLES::

    >>> import cppyy
    >>> from cppyythonizations.vector import add_vector_pythonizations
    >>> add_vector_pythonizations()
    >>> v = cppyy.gbl.std.vector[float]([1, 2, 3])
    >>> str(v)
    '[1.0, 2.0, 3.0]'

Note that this only changes `__str__`, if you also want vectors to print as
list in a Python prompt, you need to `enable_pretty_printing` from
`cppyythonizations.printing`.

    >>> v
    <cppyy.gbl.std.vector<float> object at ...>
    >>> repr(v)
    '<cppyy.gbl.std.vector<float> object at ...>'

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
        >>> from cppyythonizations.printing import enable_list_printing, enable_pretty_printing
        >>> from cppyythonizations.util import filtered
        >>> cppyy.py.add_pythonization(filtered("set<long>")(enable_list_printing), "std")
        >>> cppyy.py.add_pythonization(filtered("set<long>")(enable_pretty_printing), "std")
        >>> cppyy.gbl.std.set['long']()
        []

    """
    proxy.__str__ = lambda self: str(list(self))

def add_vector_pythonizations():
    r"""
    Enable printing of `std::vector<>` as a Python list.

    EXAMPLES::

        >>> import re
        >>> import cppyy
        >>> from cppyythonizations.util import filtered
        >>> from cppyythonizations.vector import add_vector_pythonizations
        >>> from cppyythonizations.printing import enable_pretty_printing
        >>> add_vector_pythonizations()
        >>> cppyy.py.add_pythonization(filtered(re.compile("vector<.*>"))(enable_pretty_printing), "std")
        >>> cppyy.gbl.std.vector['long']([1, 2, 3])
        [1, 2, 3]

    """
    cppyy.py.add_pythonization(filtered(re.compile("vector<.*>"))(enable_list_printing), "std")
