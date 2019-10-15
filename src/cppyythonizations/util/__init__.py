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

import cppyy

def filtered(filter=lambda proxy, name: True):
    r"""
    Decorator to make a pythonization only apply if its arguments match
    ``filter``. The filter can be an actual predicate, or a list of strings or
    regular expressions.

    It is usually advisable to use the scope parameter of add_pythonization
    instead (or at least additionally) as this implementation can be quite
    slow in comparison.

    EXAMPLES::

        >>> import cppyy
        >>> from cppyythonizations.util import filtered

    Filter for a single class::

        >>> def printer(proxy, name): proxy.__repr__ = lambda self: "pythonization applied"
        >>> cppyy.py.add_pythonization(filtered('SingleClass')(printer))
        >>> cppyy.cppdef(r'''
        ... class SingleClass {};
        ... class AnotherClass {};
        ... ''')
        True
        >>> cppyy.gbl.SingleClass()
        pythonization applied
        >>> cppyy.gbl.AnotherClass()
        <cppyy.gbl.AnotherClass object at 0x...>

    Filter for a list of classes::

        >>> cppyy.py.add_pythonization(filtered(['FirstClass', 'SecondClass'])(printer))
        >>> cppyy.cppdef(r'''
        ... class FirstClass {};
        ... class SecondClass {};
        ... class ThirdClass {};
        ... ''')
        True
        >>> cppyy.gbl.FirstClass()
        pythonization applied
        >>> cppyy.gbl.SecondClass()
        pythonization applied
        >>> cppyy.gbl.ThirdClass()
        <cppyy.gbl.ThirdClass object at 0x...>

    Filter with a regular expression::

        >>> import re
        >>> cppyy.py.add_pythonization(filtered(re.compile('.*PythonizedClass'))(printer))
        >>> cppyy.cppdef(r'''
        ... class PythonizedClass {};
        ... class UnpythonizedClass {};
        ... ''')
        True
        >>> cppyy.gbl.PythonizedClass()
        pythonization applied
        >>> cppyy.gbl.UnpythonizedClass()
        <cppyy.gbl.UnpythonizedClass object at 0x...>

    Filter with a predicate::

        >>> cppyy.py.add_pythonization(filtered(lambda proxy, name: len(name) %2 == 0)(printer))
        >>> cppyy.cppdef(r'''
        ... struct PythonizedStruct {};
        ... struct NotPythonizedStruct {};
        ... ''')
        True
        >>> cppyy.gbl.PythonizedStruct()
        pythonization applied
        >>> cppyy.gbl.NotPythonizedStruct()
        <cppyy.gbl.NotPythonizedStruct object at 0x...>

    """
    if not hasattr(filter, '__call__'):
        from collections.abc import Iterable
        if isinstance(filter, str) or not isinstance(filter, Iterable):
            filter = [filter]
        filters = list(filter)

        def filter(proxy, name):
            for filter in filters:
                if hasattr(filter, 'match'):
                    if filter.match(name):
                        return True
                else:
                    if filter == name:
                        return True
            return False
    
    def wrap(pythonization):
        def wrapped(proxy, name):
            if filter(proxy, name):
                pythonization(proxy, name)
        return wrapped

    return wrap
