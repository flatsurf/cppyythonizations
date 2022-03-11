# ********************************************************************
#  This file is part of cppyythonizations.
#
#        Copyright (C) 2020-2022 Julian Rüth
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
import os
from setuptools.command.sdist import sdist
from setuptools.command.egg_info import egg_info
from distutils.core import setup
from subprocess import check_call


class AutotoolsCommand:
    r"""
    Helpers that provide variables like the ones available to automake
    Makefiles.
    """
    @property
    def builddir(self):
        r"""
        Return the path of the build directory, equivalent to @builddir@ in automake.

        This property is only available when a build has been invoked as part of this setup.py run.
        In particular, this is the directory passed with --build-base.
        Note that "setup.py install" does not accept a --build-base so we have
        to make sure that this happens to be build/ relative to the current
        working directory during the install phase since otherwise the install
        step won't be able to find the assets that have been built by the build
        step.
        """
        if "build" not in self.distribution.command_obj:
            raise ValueError("There is no build directory since no build is being performed in this invocation of setup.py")

        return self.distribution.command_obj["build"].build_base

    @property
    def abs_builddir(self):
        r"""
        Return the absolute path of the build directory, equivalent to @abs_builddir@ in automake.

        The limitations of `builddir` apply to this property as well.
        """
        builddir = self.builddir
        if not os.path.isabs(builddir):
            builddir = os.path.join(self.abs_srcdir, builddir)

        return builddir

    @property
    def destdir(self):
        r"""
        Return the installation prefix for this package in site-packages (or the user directory.)

        This is the value that you want to pass to a configure's --prefix flag.
        Note that naturally this value is only available when setup was asked
        to install this package. In particular, this is not available when
        trying to build a wheel.

        As a consequence this value is also not available initially when
        invoking `pip install` since that tries to build a wheel first. You
        might want to invoke pip install with `--no-binary :all:` so that pip
        skips to a regular install where this value is available.
        """
        if "install" not in self.distribution.command_obj:
            raise ValueError("Cannot determine installation prefix in this build which does not install.")
        return os.path.join(self.distribution.command_obj["install"].install_lib, self.distribution.get_name())

    @property
    def abs_srcdir(self):
        r"""
        Return the absolute path of the source directory, i.e., the directory where this setup.py is.

        This is the equivalent to @abs_srcdir@ in automake.
        """
        return os.path.abspath(os.path.dirname(__file__) or ".")

    @property
    def MAKE(self):
        r"""
        Return the name of the make command which might have been overridden by
        the MAKE environment variable.
        """
        return os.getenv("MAKE", "make")


class EggInfoVPath(egg_info, AutotoolsCommand):
    r"""
    A VPATH aware egg_info for VPATH builds with Automake, inspired by
    https://blog.kevin-brown.com/programming/2014/09/24/combining-autotools-and-setuptools.html

    Builds the .egg-info in the --build-base path that was given to "build".

    For this to work, that path must be the path build/ relative to the build
    directory; see AutotoolsCommand.builddir.
    """

    def finalize_options(self):
        if "build" in self.distribution.command_obj:
            self.egg_base = self.builddir

        super().finalize_options()


class MakeDist(sdist, AutotoolsCommand):
    r"""
    Creates a source distribution for PyPI for an autoconfiscated project.
    """

    def run(self):
        if os.path.normpath(os.getcwd()) != os.path.normpath(self.abs_srcdir):
            raise NotImplementedError("A source distribution can only be created from the directory where the setup.py file resides, currently.")

        check_call([os.path.join(self.abs_srcdir, "configure"), "--without-pytest"])
        check_call([self.MAKE, "distdir"])
        super().run()


setup(
    name='cppyythonizations',
    author='Julian Rüth',
    author_email='julian.rueth@fsfe.org',
    version='1.1.3',
    url='https://github.com/flatsurf/cppyythonizations',
    packages=['cppyythonizations', 'cppyythonizations.pickling', 'cppyythonizations.util', 'cppyythonizations.operators', 'cppyythonizations.vector', 'cppyythonizations.tuple', 'cppyythonizations.printing', 'cppyythonizations.boost.type_erasure'],
    license='MIT',
    install_requires=[
        'cppyy'
    ],
    long_description="A collection of Pythonizations for cppyy",
    include_package_data=True,
    cmdclass={
        'egg_info': EggInfoVPath,
        'sdist': MakeDist,
    },
    package_dir={
        # In VPATH builds, search pyeantic relative to this setup.py file.
        '': "src" if os.path.relpath(os.path.dirname(__file__) or ".") == "." else os.path.join(os.path.relpath(os.path.dirname(__file__)), "src")
    },
)
