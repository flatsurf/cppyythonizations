# Fix C++ Operator Issues in Python

Sometimes cppyy has trouble picking up operators that are defined in C++
automatically, see https://bitbucket.org/wlav/cppyy/issues/205/boost-operators-are-not-detected or
https://bitbucket.org/wlav/cppyy/issues/93/missing-space-makes-operator-resolve-to.

While these specific issues might be fixed in your copy of cppyy, these methods
try to fill in any missing operators that are available in C++ but missing in
Python for whatever reason.
