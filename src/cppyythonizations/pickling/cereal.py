r"""
Pythonizations to support pickling of cereal-enabled C++ classes

EXAMPLES:

Enable serialization for the types in the ``doctest`` namespace::

   >>> import cppyy
   >>> from cppyythonizations.pickling.cereal import enable_cereal
   >>> cppyy.py.add_pythonization(enable_cereal, "doctest")

We define a C++ class in that namespace with the usual cereal interface::

   >>> cppyy.cppdef(r'''
   ... namespace doctest {
   ...   struct Cereal {
   ...     int x; 
   ...     template <typename Archive>
   ...     void serialize(Archive& archive) { archive(x); }
   ...   };
   ... }''')
   True

Python pickling works for this class::

   >>> from pickle import loads, dumps
   >>> demo = cppyy.gbl.doctest.Cereal()
   >>> demo.x = 1337
   >>> loads(dumps(demo)).x
   1337

This also work with smart pointers even when our class does not provide a
default constructor. However, we need an additional cereal header to support smart pointers::

    >>> def enable_smart_cereal(proxy, name):
    ...     from cppyythonizations.pickling.cereal import enable_cereal
    ...     enable_cereal(proxy, name, ["cereal/types/memory.hpp"])
    >>> from cppyythonizations.util import filtered
    >>> enable_smart_cereal = filtered('Smart')(enable_smart_cereal)
    >>> cppyy.py.add_pythonization(enable_smart_cereal)

::

    >>> cppyy.cppdef(r'''
    ... struct Smart {
    ...   Smart(int x) : x(x) {}
    ...   int x;
    ...   template <typename Archive> void serialize(Archive& archive) { archive(x); }
    ...   template <typename Archive> static void load_and_construct(Archive& archive, cereal::construct<Smart>& construct) {
    ...     int x;
    ...     archive(x);
    ...     construct(x);
    ...   }
    ... };''')
    True

    >>> obj = cppyy.gbl.std.make_shared[cppyy.gbl.Smart](1337)
    >>> loads(dumps(obj)).x
    1337

"""
# ********************************************************************
#  This file is part of cppyythonizations.
#
#        Copyright (C) 2019 Julian Rüth
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

import os.path
import cppyy

def _load_headers(headers):
    r"""
    Load ``headers`` to make (de)serialization work and return the namespace of
    the pickling helpers.

    EXAMPLES::

        >>> from cppyythonizations.pickling.cereal import _load_headers
        >>> _load_headers([])
        <namespace cppyy.gbl.cppyythonizations.pickling.cereal at 0x...>

    """
    cppyy.include(os.path.join(os.path.dirname(__file__), "cereal.hpp"))
    for header in headers:
        cppyy.include(header)

    return cppyy.gbl.cppyythonizations.pickling.cereal

def unpickle_from_cereal(t, data, headers):
    r"""
    A global unpickler for everything pickled with cereal.

    To make unpickling with ``__reduce__`` work, we need a global factory
    function that the unpickler can call to unpickle a ``t`` from ``data``.

    TESTS::

        >>> import cppyy
        >>> from cppyythonizations.pickling.cereal import enable_cereal
        >>> from cppyythonizations.util import filtered
        >>> enable_cereal = filtered('Empty')(enable_cereal)
        >>> cppyy.py.add_pythonization(enable_cereal)
        >>> cppyy.cppdef(r'''
        ... class Empty{};
        ... ''')
        True
        >>> obj = cppyy.gbl.Empty()
        >>> reduction = obj.__reduce__()
        >>> reduction[0]
        <function unpickle_from_cereal at 0x...>

    """
    return _load_headers(headers).deserialize[t](data)


def enable_cereal(proxy, name, headers=[]):
    r"""
    A `Pythonization <https://cppyy.readthedocs.io/en/latest/pythonizations.html>`
    to enable pickling through the `cereal <http://uscilab.github.io/cereal/>`
    serialization interface.

    EXAMPLES:

    This Pythonization provides pickling support for C++ types that implement
    the serialization interface of cereal::

        >>> import cppyy
        >>> from cppyythonizations.pickling.cereal import enable_cereal
        >>> cppyy.py.add_pythonization(enable_cereal, "doctest")
        >>> cppyy.cppdef(r'''
        ... namespace doctest {
        ...   struct Demo {
        ...     int x; 
        ...     template <typename Archive>
        ...     void serialize(Archive& archive) { archive(x); }
        ...   };
        ... }''')
        True

        >>> from pickle import loads, dumps
        >>> demo = cppyy.gbl.doctest.Demo()
        >>> demo.x = 1337
        >>> loads(dumps(demo)).x
        1337

    Note that we do not call back into Python when serializing so some nested
    structures do not get properly deduplicated yet when serializing::

        >>> cppyy.cppdef(r'''
        ... #include <memory>
        ... #include <cereal/types/vector.hpp>
        ... 
        ... namespace doctest {
        ...   struct Child {
        ...     std::string x;
        ...     template <typename Archive>
        ...     void serialize(Archive& archive) { archive(x); }
        ...   };
        ...   struct Parent {
        ...     std::vector<std::shared_ptr<Child>> children;
        ...     template <typename Archive>
        ...     void serialize(Archive& archive) { archive(children); }
        ...   };
        ... }
        ... ''')
        True

        >>> child = cppyy.gbl.std.make_shared[cppyy.gbl.doctest.Child]()
        >>> child.x = '0' * 1024
        >>> len(dumps(child))
        1224

    Python deduplicates the following, since it's just the same Python
    reference twice::

        >>> len(dumps([child, child]))
        1231

    Cereal deduplicates smart pointers::

        >>> parent = cppyy.gbl.doctest.Parent()
        >>> parent.children.push_back(child)
        >>> parent.children.push_back(child)
        >>> len(dumps(parent))
        1258

    However, we can not deduplicate between C++ and Python yet::

        >>> len(dumps([parent, child]))
        2427

    As a result, the unpickled objects are also not identical anymore::

        >>> parent.children[0] == child
        True
        >>> parent, child = loads(dumps((parent, child)))
        >>> parent.children[0] == child
        False

    """
    def reduce(self):
        r"""
        A generic ``__reduce__`` implementation that delegates to cereal.
        """
        ptr = self.__smartptr__()
        if ptr is not None: self = ptr

        assert cppyy.gbl.std.is_default_constructible[type(self)]().value, "only default constructible types can be handled by cereal"

        return (unpickle_from_cereal, (type(self), _load_headers(headers).serialize[type(self)](self), headers))

    proxy.__reduce__ = reduce
