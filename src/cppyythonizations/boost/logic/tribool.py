r"""
Improve interaction with boost's tribool from cppyy

EXAMPLES::

    >>> import cppyy
    >>> from cppyythonizations.boost.logic.tribool import add_tribool_pythonizations
    >>> add_tribool_pythonizations()

    >>> tribool = cppyy.gbl.boost.logic.tribool

    >>> tribool()
    false
    >>> tribool(False)
    false
    >>> tribool(True)
    true
    >>> tribool.indeterminate
    indeterminate

Note that the following does not work to detect an indeterminate state::

    >>> indeterminate = tribool.indeterminate
    >>> is_determinate = lambda x: bool(x) or not x # this would be correct in C++ but it does not work in Python
    >>> is_determinate(indeterminate)
    True

This did not work because of how Python's `not` is implemented::

    >>> bool(indeterminate)
    False
    >>> not indeterminate
    True

Instead you have to explicitly check for an indeterminate state with
`is_indeterminate`::

    >>> indeterminate.is_indeterminate()
    True

Note that you cannot check like this (same as in C++ actually)::

    >>> indeterminate == tribool.indeterminate
    indeterminate

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

from ...util import filtered

def add_tribool_pythonizations():
    cppyy.py.add_pythonization(filtered("tribool")(enable_printing), "boost::logic")
    cppyy.py.add_pythonization(filtered("tribool")(enable_indeterminate), "boost::logic")

cppyy.cppdef(r"""
#include <boost/logic/tribool.hpp>

namespace cppyythonizations::boost::logic::tribool {

static constexpr ::boost::logic::tribool indeterminate = ::boost::logic::tribool(::boost::logic::indeterminate);

}
""")

def enable_indeterminate(proxy, name):
    r"""
    Make tribool's indeterminate state and checks more readily accessible from
    Python.

    EXAMPLES::

        >>> import cppyy
        >>> from cppyythonizations.boost.logic.tribool import add_tribool_pythonizations
        >>> add_tribool_pythonizations()

        >>> tribool = cppyy.gbl.boost.logic.tribool
        >>> tribool.indeterminate
        indeterminate

        >>> tribool(True).is_indeterminate()
        False

        >>> tribool.indeterminate.is_indeterminate()
        True

    """
    proxy.indeterminate = cppyy.gbl.cppyythonizations.boost.logic.tribool.indeterminate
    proxy.is_indeterminate = lambda self: cppyy.gbl.boost.logic.indeterminate(self)

def enable_printing(proxy, name):
    r"""
    Make tribools print nicely in Python.

    Note that we do not use the builtin printing from tribool_io.hpp since it
    is too much hassle to make the stream manipulations happen in cppyy.
    """
    def to_string(tribool):
        if tribool:
            return "true"
        elif tribool.is_indeterminate():
            return "indeterminate"
        else:
            return "false"
    proxy.__repr__ = to_string
    proxy.__str__ = to_string
