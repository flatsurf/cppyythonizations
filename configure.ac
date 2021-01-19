dnl Process this file with autoconf to produce a configure script.

dnl We need at least autoconf 2.69 for this configure.ac to work.
AC_PREREQ([2.69])
AC_INIT([cppyythonizations], [1.1.3], [julian.rueth@fsfe.org])
AC_CONFIG_AUX_DIR([.])

AC_CONFIG_MACRO_DIR([m4])
AM_INIT_AUTOMAKE([foreign 1.14.1 tar-pax])

dnl We run the valgrind test-suite in make check-valgrind (if valgrind is installed)
AX_VALGRIND_DFLT([sgcheck], [off])
AX_VALGRIND_DFLT([drd], [off])
AX_VALGRIND_DFLT([helgrind], [off])
AX_VALGRIND_CHECK()

AM_PATH_PYTHON([3.6], [], [AC_MSG_ERROR([No suitable Python version found])])

dnl Our Python library relies on cppyy. It can be built without since it is a
dnl pure Python package but we cannot test it if cppyy is not present.
AC_ARG_WITH([pytest], AS_HELP_STRING([--without-pytest], [Do not run Python tests]))
AS_IF([test "x$with_pytest" != "xno"],
      [
       with_pytest=yes
       AS_IF([$PYTHON -c 'import pytest'], , AC_MSG_ERROR([pytest for make check not found; run --without-pytest to disable Python tests in make check]))
       AS_IF([$PYTHON -c 'import cppyy'], , AC_MSG_ERROR([cppyy for make check not found; run --without-pytest to disable Python tests in make check]))
      ], [])
AM_CONDITIONAL([HAVE_PYTEST], [test "x$with_pytest" = "xyes"])

AC_CONFIG_FILES([Makefile src/Makefile test/Makefile])

AC_OUTPUT

