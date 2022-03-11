r"""
Improves support for ``boost::type_erasure::any``.

EXAMPLES:

Let us consider a type erasure for any type that has an ``empty`` method, like
various STL containers::

    >>> import cppyy
    >>> cppyy.include("boost/type_erasure/any.hpp")
    >>> cppyy.cppdef(r'''
    ... #include <boost/type_erasure/member.hpp>
    ... BOOST_TYPE_ERASURE_MEMBER((has_member_empty), empty, 0);
    ... struct EmptyInterface : boost::mpl::vector<
    ...   boost::type_erasure::copy_constructible<>,
    ...   has_member_empty<bool() const>,
    ...   boost::type_erasure::typeid_<>,
    ...   boost::type_erasure::relaxed> {};
    ... using any_empty = boost::type_erasure::any<EmptyInterface>;
    ... ''')

Currently, cppyy fails to create such an ``any`` directly::

    >>> v = cppyy.gbl.std.vector[int]()
    >>> cppyy.gbl.any_empty(v)
    Traceback (most recent call last):
    ...
    TypeError: Template method resolution failed...

This module provides a helper to create such an ``any``::

    >>> from cppyythonizations.boost.type_erasure import make_any
    >>> erased_vector = make_any(cppyy.gbl.any_empty)(v)

In this exmple, cppyy sees the ``empty`` method and can call it directly::

    >>> hasattr(erased_vector, 'empty')
    >>> erased_vector.empty()
    True

However, in more complicated cases, cppyy fails to see such methods::

    >>> cppyy.cppdef(r'''
    ... BOOST_TYPE_ERASURE_MEMBER((has_member_identity), identity, 1);
    ...
    ... struct IdentityInterface;
    ...
    ... using any_identity = boost::type_erasure::any<IdentityInterface>;
    ...
    ... struct IdentityInterface : boost::mpl::vector<
    ...   boost::type_erasure::copy_constructible<>,
    ...   has_member_identity<any_identity(any_identity)>,
    ...   boost::type_erasure::typeid_<>,
    ...   boost::type_erasure::relaxed> {};
    ...
    ... struct Identity {
    ...   any_identity identity(any_identity x) { return x; }
    ... };
    ... ''')

    >>> identity = cppyy.gbl.Identity()
    >>> erased_identity = make_any(cppyy.gbl.any_identity)(identity)
    >>> hasattr(erased_identity, "identity")
    False

These methods can be explicitly made visible::

    >>> from cppyythonizations.util import filtered
    >>> from cppyythonizations.boost.type_erasure import expose
    >>> cppyy.py.add_pythonization(filtered("any<IdentityInterface2,boost::type_erasure::_self>")(expose("identity")), "boost::type_erasure")

    >>> cppyy.cppdef(r'''
    ... struct IdentityInterface2 : IdentityInterface {};
    ... using any_identity2 = boost::type_erasure::any<IdentityInterface2>;
    ... ''')

    >>> erased_identity2 = make_any(cppyy.gbl.any_identity2)(identity)
    >>> hasattr(erased_identity2, "identity")
    True
    >>> erased_identity2.identity(erased_identity)
    <cppyy.gbl.boost.type_erasure.any<IdentityInterface,boost::type_erasure::_self> object at 0x...

"""
# ********************************************************************
#  This file is part of cppyythonizations.
#
#        Copyright (C) 2022 Julian Rüth
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

cppyy.cppdef(r'''
namespace cppyythonizations {
namespace boost {
namespace type_erasure {

template <typename ANY>
struct any {
    template <typename T>
    static auto make(T&& value) {
        ANY x = std::forward<T>(value);
        return x;
    }
};

}
}
}
''')


def make_any(type):
    r"""
    Return a factory that creates a ``type`` from its argument.

    EXAMPLES::

        >>> import cppyy
        >>> cppyy.include("boost/type_erasure/any.hpp")
        >>> cppyy.cppdef(r'''
        ... #include <boost/type_erasure/member.hpp>
        ... BOOST_TYPE_ERASURE_MEMBER((has_member_empty), empty, 0);
        ... struct EmptyInterface : boost::mpl::vector<
        ...   boost::type_erasure::copy_constructible<>,
        ...   has_member_empty<bool() const>,
        ...   boost::type_erasure::typeid_<>,
        ...   boost::type_erasure::relaxed> {};
        ... using any_empty = boost::type_erasure::any<EmptyInterface>;
        ... ''')

        >>> make_any(cppyy.gbl.any_empty)(cppyy.gbl.std.vector[int]())

    """
    return cppyy.gbl.cppyythonizations.boost.type_erasure.any[type].make


def expose(name, cpp_name=None):
    r"""
    Return a Pythonization that exposes the method ``cpp_name`` as the method ``name``.

    EXAMPLES:

    Normally, methods are invoked as ``self.name(...)``. However, in some
    cases, this does not work, e.g., when invoking a free operator. In such
    cases, ``cpp_name`` can be set to generate the calling code::

        >>> import cppyy
        >>> cppyy.cppdef(r'''
        ... #include <boost/type_erasure/operators.hpp>
        ...
        ... struct EqualityComparableInterface;
        ...
        ... using any_equality_comparable = boost::type_erasure::any<EqualityComparableInterface>;
        ...
        ... struct EqualityComparableInterface : boost::mpl::vector<
        ...   boost::type_erasure::copy_constructible<>,
        ...   boost::type_erasure::equality_comparable<>,
        ...   boost::type_erasure::typeid_<>,
        ...   boost::type_erasure::relaxed> {};
        ...
        ... struct EqualityComparable {
        ...   bool operator==(const EqualityComparable& rhs) const { return this == &rhs; }
        ... };
        ... ''')

        >>> from cppyythonizations.util import filtered
        >>> from cppyythonizations.boost.type_erasure import expose
        >>> cppyy.py.add_pythonization(filtered("any<EqualityComparableInterface,boost::type_erasure::_self>")(expose("eq", lambda self, args: f"[](auto& lhs, auto& rhs) {{ return lhs == rhs; }}({self}, {args})")), "boost::type_erasure")

        >>> equality_comparable = cppyy.gbl.EqualityComparable()
        >>> from cppyythonizations.boost.type_erasure import make_any
        >>> erased_equality_comparable = make_any(cppyy.gbl.any_equality_comparable)(equality_comparable)
        >>> erased_equality_comparable.eq(erased_equality_comparable)
        True

    """
    if cpp_name is None:
        cpp_name = name

    if not callable(cpp_name):
        def create_code(self, args, cpp_name=cpp_name):
            return f"{self}.{cpp_name}({args})"
        cpp_name = create_code

    function = f"expose_{name}_{''.join(c for c in cpp_name('', '') if c.isalnum())}"

    if not hasattr(cppyy.gbl.cppyythonizations.boost.type_erasure, function):
        cppyy.cppdef(f"""
        namespace cppyythonizations {{
        namespace boost {{
        namespace type_erasure {{
        template <typename T, typename ...Args>
        auto {function}(T&& t, Args&& ...args) {{
            return {cpp_name('t', 'std::forward<Args>(args)...')};
        }}
        }}
        }}
        }}
        """)

    function = getattr(cppyy.gbl.cppyythonizations.boost.type_erasure, function)

    from cppyythonizations.util import add_method
    return add_method(name)(lambda self, *args: function(self, *args))
