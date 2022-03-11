# ********************************************************************
#  This file is part of cppyythonizations.
#
#        Copyright (C) 2021 Julian Rüth
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

from rever.activity import Activity

class AutoPyPI(Activity):
    def __init__(self, **kwargs):
        super().__init__(
          name="autopypi",
          desc = "Run setup.py in an autoconfiscated Python package and upload a bdist wheel to PyPI",
          requires = {"commands": {"make": "make", "twine": "twine"}},
          func = self._func,
        )

    def _func(self, root=".", commands=["bdist_wheel"]):
        import os.path
        root = os.path.abspath(root)

        from tempfile import TemporaryDirectory
        from xonsh.dirstack import DIRSTACK
        with TemporaryDirectory() as tmp:
            ./bootstrap
            pushd @(tmp)
            @(DIRSTACK[-1])/configure
            make

            pushd @(root)
            $PYTHON setup.py @(commands)
            twine upload --sign dist/*
            popd

            popd
        return True
    
$DAG['autopypi'] = AutoPyPI()
