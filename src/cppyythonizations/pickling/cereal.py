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

This also works for objects that implement the minimal serialization protocol::

    >>> cppyy.cppdef(r'''
    ... namespace doctest {
    ... struct Minimal {
    ...   Minimal() : x(0) {}
    ...   Minimal(int x) : x(x) {}
    ...   int x;
    ...   template <typename Archive> int save_minimal(const Archive&) const { return x; }
    ...   template <typename Archive> void load_minimal(const Archive&, const int& x) { this->x = x; }
    ... };
    ... }''')
    True

    >>> minimal = cppyy.gbl.doctest.Minimal(1337)
    >>> loads(dumps(minimal)).x == minimal.x
    True

"""
# ********************************************************************
#  This file is part of cppyythonizations.
#
#        Copyright (C) 2019-2020 Julian Rüth
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
import os, os.path, sys

# Make sure cppyy loads our own patched cereal headers to
# work around
# https://bitbucket.org/wlav/cppyy/issues/201/scope-of-static-variables
cppyy.include(os.path.join(os.path.dirname(__file__), '..', 'include/cereal/details/static_object.hpp'))

import cppyy

import json

SMARTPTR_KEY = "__smartptr__"

def _load_headers(headers):
    r"""
    Load ``headers`` to make (de)serialization work and return the namespace of
    the pickling helpers.

    EXAMPLES::

        >>> from cppyythonizations.pickling.cereal import _load_headers
        >>> _load_headers([])
        <namespace cppyy.gbl.cppyythonizations.pickling.cereal at 0x...>

    TESTS:

    Check that cereal's polymorphism support works, i.e., that we worked around
    https://bitbucket.org/wlav/cppyy/issues/201/scope-of-static-variables
    correctly::

        >>> import cppyy
        >>> from cppyythonizations.pickling.cereal import enable_cereal
        >>> from cppyythonizations.util import filtered
        >>> enable_cereal = filtered('Base')(enable_cereal)
        >>> cppyy.py.add_pythonization(enable_cereal)
        >>> cppyy.cppdef(r'''
        ... #include <cereal/types/memory.hpp>
        ... struct Base {
        ...   virtual int f() = 0;
        ...   template <typename Archive>
        ...   void serialize(Archive&) {}
        ... };
        ... struct Derived : public Base {
        ...   int f() override { return 1337; }
        ...   template <typename Archive>
        ...   void serialize(Archive& archive) {
        ...     archive(cereal::base_class<Base>(this));
        ...   }
        ... };
        ... CEREAL_REGISTER_TYPE(Derived);
        ... ''')
        True
        >>> cppyy.include('memory')
        True
        >>> derived = cppyy.gbl.std.make_unique['Derived']()
        >>> derived = cppyy.gbl.std.unique_ptr['Base'](cppyy.gbl.std.move(derived.__smartptr__()))
        >>> derived.f()
        1337
        >>> from pickle import loads, dumps
        >>> derived = loads(dumps(derived))
        >>> derived.f()
        1337

    """
    cppyy.include(os.path.join(os.path.dirname(__file__), "cereal.hpp"))
    for header in headers:
        if callable(header):
            header()
        else:
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
    if isinstance(data, dict) and SMARTPTR_KEY in data:
        t = data[SMARTPTR_KEY]
        del data[SMARTPTR_KEY]
    data = json.dumps({ "cereal": data })

    return _load_headers(headers).deserialize[t](data)


def enable_cereal(proxy, name, headers=[], yaml_tag=None):
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
        ... #include <cereal/cereal.hpp>
        ... namespace doctest {
        ...   struct Demo {
        ...     int x; 
        ...     template <typename Archive>
        ...     void serialize(Archive& archive) { archive(::cereal::make_nvp("x", x)); }
        ...     bool operator==(const Demo& rhs) { return x == rhs.x; }
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
        >>> child.x = 'DATA'
        >>> dumps(child, protocol=4)
        b'\x80\x04\x95\xcf\x00\x00\x00\x00\x00\x00\x00\x8c!cppyythonizations.pickling.cereal\x94\x8c\x14unpickle_from_cereal\x94\x93\x94\x8c\x11cppyy.gbl.doctest\x94\x8c\x05Child\x94\x93\x94}\x94(\x8c\x0bptr_wrapper\x94}\x94(\x8c\x02id\x94\x8a\x05\x01\x00\x00\x80\x00\x8c\x04data\x94}\x94\x8c\x06value0\x94\x8c\x04DATA\x94su\x8c\x0c__smartptr__\x94\x8c\x1fstd::shared_ptr<doctest::Child>\x94u]\x94\x87\x94R\x94.'
        >>> len(_)
        218

    Python deduplicates the following, since it's just the same Python
    reference twice::

        >>> dumps([child] * 8, protocol=4)
        b'\x80\x04\x95\xe1\x00\x00\x00\x00\x00\x00\x00]\x94(\x8c!cppyythonizations.pickling.cereal\x94\x8c\x14unpickle_from_cereal\x94\x93\x94\x8c\x11cppyy.gbl.doctest\x94\x8c\x05Child\x94\x93\x94}\x94(\x8c\x0bptr_wrapper\x94}\x94(\x8c\x02id\x94\x8a\x05\x01\x00\x00\x80\x00\x8c\x04data\x94}\x94\x8c\x06value0\x94\x8c\x04DATA\x94su\x8c\x0c__smartptr__\x94\x8c\x1fstd::shared_ptr<doctest::Child>\x94u]\x94\x87\x94R\x94h\x13h\x13h\x13h\x13h\x13h\x13h\x13e.'
        >>> len(_)
        236

    Cereal deduplicates smart pointers::

        >>> parent = cppyy.gbl.doctest.Parent()
        >>> parent.children.push_back(child)
        >>> parent.children.push_back(child)
        >>> len(dumps(parent, protocol=4))
        190

    However, we can not deduplicate between C++ and Python yet::

        >>> len(dumps([parent, child], protocol=4))
        341

    As a result, the unpickled objects are also not identical anymore::

        >>> parent.children[0] == child
        True
        >>> parent, child = loads(dumps((parent, child)))
        >>> parent.children[0] == child
        False

    There are also more readable dump formats such as a JSON dump::

        >>> print(demo.to_json())
        {"x": 1337}
        >>> type(demo).from_json(demo.to_json()) == demo
        True

    and YAML dumps::

        >>> from ruamel.yaml import YAML
        >>> yaml = YAML()
        >>> yaml.register_class(type(demo))
        <class cppyy.gbl.doctest.Demo ...>
        >>> yaml.dump(demo, sys.stdout)
        !cppyythonizations/cereal:doctest::Demo
        x: 1337

        >>> from io import StringIO
        >>> yaml = YAML()
        >>> yaml.register_class(type(demo))
        <class cppyy.gbl.doctest.Demo ...>
        >>> buffer = StringIO()
        >>> yaml.dump(demo, buffer)
        >>> buffer.seek(0)
        0
        >>> yaml.load(buffer).x == demo.x
        True

    Note that since we integrate with ruamel.yaml, graphs of Python objects can
    be rendered as YAML::

        >>> yaml.dump([demo, demo], sys.stdout)
        - &id001 !cppyythonizations/cereal:doctest::Demo
          x: 1337
        - *id001


    """
    def reduce(self):
        r"""
        A generic ``__reduce__`` implementation that delegates to cereal.
        """
        if not self.__smartptr__():
            assert cppyy.gbl.std.is_default_constructible[type(self)]().value, "only default constructible types can be handled by cereal but %s is not default constructible; you might wrap your type into a smart pointer or make it default constructible"%(type(self),)

        ptr = self.__smartptr__()
        
        cereal = _load_headers(headers).serialize[type(ptr or self)](ptr or self)
        cereal = json.loads(cereal)
        cereal = cereal["cereal"]

        assert not isinstance(cereal, dict) or SMARTPTR_KEY not in cereal, "%s has a special meaning in serialization and may not be used in cereal::make_nvp"%(SMARTPTR_KEY,)
        if ptr:
            import base64
            cereal[SMARTPTR_KEY] = type(ptr).__cpp_name__
        
        return (unpickle_from_cereal, (type(self), cereal, headers))

    def to_json(self):
        r"""
        Return a JSON string representing this object.
        """
        return json.dumps(self.__reduce__()[1][1])

    @classmethod
    def from_json(cls, data):
        r"""
        Create an object from a JSON string.
        """
        return unpickle_from_cereal(cls, json.loads(data), headers)

    @classmethod
    def to_yaml(cls, representer, obj):
        r"""
        Return a proxy object ``obj`` as YAML.
        """
        return representer.represent_mapping(cls.yaml_tag, obj.__reduce__()[1][1])

    @classmethod
    def from_yaml(cls, constructor, obj):
        r"""
        Return a proxy object from the serialized data in ``obj``.
        """
        from ruamel.yaml.comments import CommentedMap
        data = CommentedMap()
        constructor.construct_mapping(obj, data)
        return cls.from_json(json.dumps(dict(data)))

    proxy.__reduce__ = reduce
    proxy.to_json = to_json
    proxy.from_json = from_json
    proxy.yaml_tag = yaml_tag or '!cppyythonizations/cereal:%s'%(proxy.__cpp_name__.replace(' ', ''))
    proxy.to_yaml = to_yaml
    proxy.from_yaml = from_yaml
