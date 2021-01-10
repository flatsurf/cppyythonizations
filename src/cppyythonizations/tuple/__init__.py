r"""
Modifies some aspects std::tuple such as printing and indexing.

EXAMPLES::

    >>> import cppyy
    >>> from cppyythonizations.tuple import add_tuple_pythonizations
    >>> add_tuple_pythonizations()
    >>> t = cppyy.gbl.std.tuple[int, str, float](13, "x", 3.7)
    >>> str(t)
    "(13, b'x', 3.7...)"

Note that this only changes `__str__`, if you also want tuples to print as
Python tuples in a Python prompt, you need to `enable_pretty_printing` from
`cppyythonizations.printing`.

    >>> t
    <cppyy.gbl.std.tuple<int,std::string,float> object at ...>
    >>> repr(t)
    '<cppyy.gbl.std.tuple<int,std::string,float> object at ...>'

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

def enable_tuple_printing(proxy, name):
    r"""
    Print proxy objects as Python tuples.

    EXAMPLES::

        >>> import cppyy
        >>> from cppyythonizations.tuple import enable_tuple_printing
        >>> from cppyythonizations.printing import enable_pretty_printing
        >>> from cppyythonizations.util import filtered
        >>> cppyy.py.add_pythonization(filtered("tuple<int, float>")(enable_tuple_printing), "std")
        >>> cppyy.py.add_pythonization(filtered("tuple<int, float>")(enable_tuple_printing), "std")
        >>> cppyy.gbl.std.tuple[int, float](1, 2)
        (1, 2.0)

    """
    proxy.__str__ = lambda self: str(tuple(self))


def enable_tuple_indexing(proxy, name):
    r"""
    Allowing indexing into tuples with the [] operator.

    Actually, tuples come with an implementation of ``__getitem__`` out of the
    box in cppyy. However, this implementation vanishes once we add a
    Pythonization, see
    https://bitbucket.org/wlav/cppyy/issues/272/pythonization-on-tuple-erases-__getitem__.

    EXAMPLES::

        >>> import cppyy
        >>> from cppyythonizations.tuple import enable_tuple_indexing
        >>> from cppyythonizations.util import filtered
        >>> cppyy.py.add_pythonization(filtered("tuple<string, string>")(enable_tuple_indexing), "std")
        >>> t = cppyy.gbl.std.tuple[str, str]("a", "b")
        >>> t[0]
        b'a'
        >>> t[1]
        b'b'
        >>> t[2]
        Traceback (most recent call last):
        ...
        IndexError: tuple index out of range
        >>> list(t)
        [b'a', b'b']
        >>> len(t)
        2
        >>> t[::2]
        (b'a',)

    """
    def getitem(self, key):
        size = len(self)
        def get(index):
            if index >= 0:
                if index >= size:
                    raise IndexError("tuple index out of range")
                return cppyy.gbl.std.get[index](self)
            else:
                if -index > size:
                    raise IndexError("tuple index out of range")
                return get(size - index)

        if isinstance(key, slice):
           return tuple(get(i) for i in list(range(size))[key])
        else:
           return get(int(key))

    proxy.__getitem__ = getitem
    proxy.__len__ = lambda self: cppyy.gbl.std.tuple_size[proxy].value


def add_tuple_pythonizations():
    r"""
    Enable printing of `std::tuple<>` as a Python tuple, and Python tuple indexing.

    EXAMPLES::

        >>> import re
        >>> import cppyy
        >>> from cppyythonizations.tuple import add_tuple_pythonizations
        >>> from cppyythonizations.printing import enable_pretty_printing
        >>> add_tuple_pythonizations()
        >>> cppyy.py.add_pythonization(filtered(re.compile("tuple<.*>"))(enable_pretty_printing), "std")
        >>> cppyy.gbl.std.tuple[int, str](1, "x")
        (1, b'x')
        >>> _[1]
        b'x'

    """
    cppyy.py.add_pythonization(filtered(re.compile("tuple<.*>"))(enable_tuple_printing), "std")
    cppyy.py.add_pythonization(filtered(re.compile("tuple<.*>"))(enable_tuple_indexing), "std")
