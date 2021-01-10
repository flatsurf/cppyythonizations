r"""
Pythonizations to support pickling of cereal-enabled C++ classes

WARNING:

  As of mid 2020, we consider this serialization format, in particular the YAML
  format, unstable and experimental. Expect it to still change frequently.

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
YAML_TAG_PREFIX = "tag:cppyy.dev,2020:cereal#"
YAML_TAG_REWRITE_MAP = "tag:cppyy.dev,2020:map#"


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


def to_yaml(cls, representer, obj):
    r"""
    Return a cppyy proxy object ``obj`` as YAML.
    """
    reduction = obj.__reduce__()[1][1]
    if isinstance(reduction, list):
        ret = representer.represent_sequence(cls.yaml_tag, reduction)
    else:
        ret = representer.represent_mapping(cls.yaml_tag, reduction)

    ret = simplify(ret)
    return ret


def simplify(node):
    r"""
    Perform some simplifications on the YAML tree rooted at node. Mostly, this
    attempts to make things more compact or more readable, working around some
    oddities of cereal or inefficiencies that come from the original JSON format.
    """
    node = simplify_mappings(node)
    return node


def revert_simplifications(node):
    r"""
    Undo the changes performed by `simplify`.
    """
    node = revert_mappings(node)
    return node


def simplify_mappings(node):
    r"""
    Cereal saves a map very explicitly as a list of key value pairs,
    i.e.,`[{key: "abc", value: 1}, {key: "def", value: 2}]`. For JSON
    that's very reasonable since keys cannot have arbitrary types but
    in YAML we do not have that limitation so we detect and rewrite
    such mappings.
    """
    from ruamel.yaml.nodes import SequenceNode, MappingNode, ScalarNode
    def to_key_value(pairs):
        if len(pairs) != 2:
            return False

        key, value = pairs
        if len(key) != 2:
            return False
        if len(value) != 2:
            return False

        if not isinstance(key[0], ScalarNode) or key[0].tag != 'tag:yaml.org,2002:str' or key[0].value != 'key':
            return False
        if not isinstance(value[0], ScalarNode) or value[0].tag != 'tag:yaml.org,2002:str' or value[0].value != 'value':
            return False

        return (simplify_mappings(key[1]), simplify_mappings(value[1]))

    def to_map(values):
        map = []

        for value in values:
            if not isinstance(value, MappingNode):
                return False
            if value.tag != 'tag:yaml.org,2002:map':
                return False
            kv = to_key_value(value.value)
            if not kv:
                return False

            map.append(kv)

        return map

    if isinstance(node, SequenceNode):
        map = to_map(node.value)
        if map:
            node = MappingNode(tag="%s%s"%(YAML_TAG_REWRITE_MAP, node.tag if node.tag != 'tag:yaml.org,2002:seq' else ''), value=map, start_mark=node.start_mark, end_mark=node.end_mark, comment=node.comment, anchor=node.anchor)
        else:
            node.value = [simplify_mappings(value) for value in node.value]
    elif isinstance(node, MappingNode):
        node.value = [(simplify_mappings(key), simplify_mappings(value)) for (key, value) in node.value]

    return node


def revert_mappings(node):
    r"""
    Undo the effect of simplify_mappings.
    """
    from ruamel.yaml.nodes import SequenceNode, MappingNode, ScalarNode
    if isinstance(node, MappingNode):
        if node.tag.startswith(YAML_TAG_REWRITE_MAP):
            tag = node.tag[len(YAML_TAG_REWRITE_MAP):] or "tag:yaml.org,2002:seq"
            node = SequenceNode(tag=tag, value=[
                MappingNode(tag="tag:yaml.org,2002:map", value=[
                    (ScalarNode(tag="tag:yaml.org,2002:str", value="key", start_mark=key.start_mark, end_mark=key.end_mark), revert_mappings(key)),
                    (ScalarNode(tag="tag:yaml.org,2002:str", value="value", start_mark=value.start_mark, end_mark=value.end_mark), revert_mappings(value)),
                ], start_mark=key.start_mark, end_mark=value.end_mark) for (key, value) in node.value
            ], start_mark=node.start_mark, end_mark=node.end_mark, comment=node.comment, anchor=node.anchor)
        else:
            node.value = [(revert_mappings(key), revert_mappings(value)) for (key, value) in node.value]
    elif isinstance(node, SequenceNode):
        node.value = [revert_mappings(value) for value in node.value]

    return node


def multi_construct_from_yaml(constructor, tag_suffix, node):
    r"""
    Reconstruct the cppyy wrapper from the YAML tree ``node`` whose type is
    given by ``type_suffix``.
    """
    # This might be a CPython specific approach and there might be a more
    # generic way for doing this. (One could of course compile a typedef and
    # read it but that seems very inefficient.)
    cpptype = cppyy._backend.CreateScopeProxy(unescape_type_name(tag_suffix))
    return cpptype.from_yaml(constructor, node)


def multi_construct_from_yaml_map(constructor, tag_suffix, node):
    r"""
    Reconstruct the cppyy wrapper from the YAML tree ``node`` whose types is
    given by ``type_suffix``.

    This is a specialized version of ``multi_construct_from_yaml`` which works
    for map types mangled by ``simplify_mappings``.
    """
    if tag_suffix.startswith(YAML_TAG_PREFIX):
        return multi_construct_from_yaml(constructor, tag_suffix[len(YAML_TAG_PREFIX):], node)
    else:
        return constructor.construct_non_recursive_object(tag_suffix, revert_simplifications(node))


def from_yaml(cls, constructor, node):
    r"""
    Return a proxy object from the serialized data in ``node``.
    """
    def construct_value(node):
        from ruamel.yaml.nodes import SequenceNode, ScalarNode
        if isinstance(node, SequenceNode):
            return [construct_value(v) for v in node.value]
        if isinstance(node, ScalarNode):
            return constructor.construct_object(node, deep=True)
        else:
            data = constructor.loader.map()
            constructor.construct_mapping(node, data, deep=True)
            return dict(data)

    node = revert_simplifications(node)

    value = construct_value(node)

    return cls.from_json(json.dumps(value))


def to_json(self):
    r"""
    Return a JSON string representing this object.
    """
    return json.dumps(self.__reduce__()[1][1])


def from_json(cls, data, headers):
    r"""
    Create an object from a JSON string.
    """
    return unpickle_from_cereal(cls, json.loads(data), headers)


def escape_type_name(name):
    r"""
    Escapes a type name to conform with RFC 3986.

    >>> from cppyythonizations.pickling.cereal import escape_type_name
    >>> escape_type_name('int')
    'int'
    >>> escape_type_name('vector<vector<int> >')
    'vector[vector[int]]'
    >>> escape_type_name('vector<int[3]>')
    'vector[int+[+3+]+]'
    """
    return name.replace(' ', '').replace('[', '+[+').replace(']', '+]+').replace('<', '[').replace('>', ']')


def unescape_type_name(name):
    r"""
    Inverse (modulo white-space) of `escape_type_name`.

    >>> from cppyythonizations.pickling.cereal import escape_type_name, unescape_type_name
    >>> unescape_type_name(escape_type_name('int'))
    'int'
    >>> unescape_type_name(escape_type_name('vector<vector<int> >'))
    'vector<vector<int>>'
    >>> unescape_type_name(escape_type_name('vector<int[3]>'))
    'vector<int[3]>'
    """
    return name.replace(']', '>').replace('[', '<').replace('+<+', '[').replace('+>+', ']')


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

        >>> from cppyythonizations.pickling.cereal import add_cereal
        >>> from ruamel.yaml import YAML
        >>> yaml = YAML()
        >>> add_cereal(yaml)
        >>> yaml.register_class(type(demo))
        <class cppyy.gbl.doctest.Demo ...>
        >>> yaml.dump(demo, sys.stdout)
        %TAG !cereal! tag:cppyy.dev,2020:cereal#
        --- !cereal!doctest::Demo
        x: 1337

    TESTS:

    A simple helper function, to dump an object and then load it again::

        >>> def loadsdumps(obj):
        ...     dump = obj.to_json()
        ...     load = type(obj).from_json(dump)
        ...     if type(load) != type(obj) or load != obj: raise Exception("%r dumped to %r which loaded to %r but these two are not equal"%(obj, dump, load))
        ...     yaml = YAML()
        ...     add_cereal(yaml)
        ...     yaml.register_class(type(obj))
        ...     from io import StringIO
        ...     buffer = StringIO()
        ...     yaml.dump(obj, buffer)
        ...     buffer.seek(0)
        ...     dump = buffer.read().strip()
        ...     print(dump)
        ...     buffer.seek(0)
        ...     load = yaml.load(buffer)
        ...     if type(load) != type(obj) or load != obj: raise Exception("%r dumped to %r which loaded to %r but these two are not equal"%(obj, dump, load))

    Our demo object can be dumped and loaded::

        >>> loadsdumps(demo)
        %TAG !cereal! tag:cppyy.dev,2020:cereal#
        --- !cereal!doctest::Demo
        x: 1337

    Note that since we integrate with ruamel.yaml, graphs of Python objects can
    be rendered as YAML::

        >>> yaml.dump([demo, demo], sys.stdout)
        %TAG !cereal! tag:cppyy.dev,2020:cereal#
        ---
        - &id001 !cereal!doctest::Demo
          x: 1337
        - *id001

    We can serialize common types such as `std::vector` when writing out YAML::

        >>> from cppyythonizations.util import filtered
        >>> cppyy.include("cereal/types/vector.hpp")
        True
        >>> cppyy.py.add_pythonization(filtered("vector<int>")(enable_cereal), "std")
        >>> v = cppyy.gbl.std.vector[int]([1, 2, 3])
        >>> loadsdumps(v)
        %TAG !cereal! tag:cppyy.dev,2020:cereal#
        --- !cereal!std::vector[int]
        - 1
        - 2
        - 3

    We also serialize `std::map` and `std::unordered_map`::

        >>> cppyy.include("cereal/types/map.hpp")
        True
        >>> cppyy.py.add_pythonization(filtered("map<int,int>")(enable_cereal), "std")
        >>> m = cppyy.gbl.std.map[int, int]()
        >>> m[1] = 2
        >>> loadsdumps(m)
        %TAG !cereal! tag:cppyy.dev,2020:cereal#
        --- !<tag:cppyy.dev,2020:map#tag:cppyy.dev,2020:cereal#std::map[int,int]>
        1: 2

        >>> cppyy.include("cereal/types/unordered_map.hpp")
        True
        >>> cppyy.py.add_pythonization(filtered("unordered_map<int,int>")(enable_cereal), "std")
        >>> m = cppyy.gbl.std.unordered_map[int, int]()
        >>> m[1] = 2
        >>> loadsdumps(m)
        %TAG !cereal! tag:cppyy.dev,2020:cereal#
        --- !<tag:cppyy.dev,2020:map#tag:cppyy.dev,2020:cereal#std::unordered_map[int,int]>
        1: 2

    And `std::set` and `std::unordered_set`::

        >>> cppyy.include("cereal/types/set.hpp")
        True
        >>> cppyy.py.add_pythonization(filtered("set<int>")(enable_cereal), "std")
        >>> s = cppyy.gbl.std.set[int]()
        >>> _ = s.insert(1)
        >>> loadsdumps(s)
        %TAG !cereal! tag:cppyy.dev,2020:cereal#
        --- !cereal!std::set[int]
        - 1

        >>> cppyy.include("cereal/types/unordered_set.hpp")
        True
        >>> cppyy.py.add_pythonization(filtered("unordered_set<int>")(enable_cereal), "std")
        >>> s = cppyy.gbl.std.unordered_set[int]()
        >>> _ = s.insert(1)
        >>> loadsdumps(s)
        %TAG !cereal! tag:cppyy.dev,2020:cereal#
        --- !cereal!std::unordered_set[int]
        - 1

    Complex standard types can also be serialized::

        >>> cppyy.py.add_pythonization(filtered("map<std::set<int>,std::map<int,std::string> >")(enable_cereal), "std")
        >>> m = cppyy.gbl.std.map[cppyy.gbl.std.set[int], cppyy.gbl.std.map[int, str]]()
        >>> m[cppyy.gbl.std.set[int]([1, 2, 3])][1337] = "A"
        >>> loadsdumps(m)
        %TAG !cereal! tag:cppyy.dev,2020:cereal#
        --- !<tag:cppyy.dev,2020:map#tag:cppyy.dev,2020:cereal#std::map[std::set[int],std::map[int,std::string]]>
        ? - 1
          - 2
          - 3
        : !<tag:cppyy.dev,2020:map#>
          1337: A

    """
    def reduce(self):
        r"""
        A generic ``__reduce__`` implementation that delegates to cereal.
        """
        if not self.__smartptr__():
            assert cppyy.gbl.std.is_default_constructible[type(self)]().value, "only default constructible types can be handled by cereal but %s is not default constructible; you might wrap your type into a smart pointer or make it default constructible"%(type(self),)

        ptr = self.__smartptr__()

        cereal = _load_headers(headers).serialize[type(ptr or self)](ptr or self)
        cereal = json.loads(bytes(cereal))
        cereal = cereal["cereal"]

        assert not isinstance(cereal, dict) or SMARTPTR_KEY not in cereal, "%s has a special meaning in serialization and may not be used in cereal::make_nvp"%(SMARTPTR_KEY,)
        if ptr:
            import base64
            cereal[SMARTPTR_KEY] = type(ptr).__cpp_name__

        return (unpickle_from_cereal, (type(self), cereal, headers))

    proxy.__reduce__ = reduce
    proxy.to_json = to_json
    proxy.from_json = classmethod(lambda cls, data: from_json(cls, data, headers))
    proxy.yaml_tag = yaml_tag or '%s%s'%(YAML_TAG_PREFIX, escape_type_name(proxy.__cpp_name__))
    proxy.to_yaml = classmethod(to_yaml)
    proxy.from_yaml = classmethod(from_yaml)


def add_cereal(yaml, handle="!cereal!"):
    r"""
    Enable cereal support on the ruamel.yaml loader ``yaml``.

    This registers our TAG prefix and registers some multi-constructors so cppyy types can be loaded.
    """
    yaml.constructor.add_multi_constructor(YAML_TAG_PREFIX, multi_construct_from_yaml)
    if handle:
        # Unfortunately, ruamel.yaml ignores its own tags when looking up
        # constructors. It's the responsibility of the parser to resolve the
        # tag but the (default) RoundTripParser does not mangle tags at all.
        # This appears to be a bug in ruamel.yaml, the constructor lookup
        # should honor global %TAG% directives.
        # Therefore, we need to manually register our handle as a
        # multi-constructor here.
        yaml.constructor.add_multi_constructor(handle, multi_construct_from_yaml)

    yaml.constructor.add_multi_constructor(YAML_TAG_REWRITE_MAP, multi_construct_from_yaml_map)

    if handle:
        if yaml.tags is None:
            yaml.tags = {}
        if handle not in yaml.tags:
            yaml.tags[handle] = YAML_TAG_PREFIX
