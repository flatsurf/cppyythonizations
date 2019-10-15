[![Build Status](https://dev.azure.com/flatsurf/conda/_apis/build/status/flatsurf.cppyythonizations?branchName=master)](https://dev.azure.com/flatsurf/conda/_build/latest?definitionId=7&branchName=master)
![Windows disabled](https://img.shields.io/badge/Windows-disabled-lightgrey.svg)
![ppc64le disabled](https://img.shields.io/badge/ppc64le-disabled-lightgrey.svg)

A collection of [Pythonizations](https://cppyy.readthedocs.io/en/latest/pythonizations.html) for [cppyy](https://cppyy.readthedocs.io/en/latest/index.html).

These mostly work around known bugs/limitations of cppyy or provide some
reusable extensions such as Python pickling of C++ classes.

## Current Release Info

We build and release this package with every push to the master branch. These releases are considered unstable and highly
experimental. There are no stable releases yet.

| Name | Downloads | Version | Platforms |
| --- | --- | --- | --- |
| [![Nightly Build](https://img.shields.io/badge/recipe-cppyythonizations-green.svg)](https://anaconda.org/flatsurf/cppyythonizations) | [![Conda Downloads](https://img.shields.io/conda/dn/flatsurf/cppyythonizations.svg)](https://anaconda.org/flatsurf/cppyythonizations) | [![Conda Version](https://img.shields.io/conda/vn/flatsurf/cppyythonizations.svg)](https://anaconda.org/flatsurf/cppyythonizations) | [![Conda Platforms](https://img.shields.io/conda/pn/flatsurf/cppyythonizations.svg)](https://anaconda.org/flatsurf/cppyythonizations) |

## Install with Conda

You can install this package with conda. Download and install [Miniconda](https://conda.io/miniconda.html), then run

```
conda config --add channels conda-forge
conda create -n cppyy -c flatsurf cppyy cppyythonizations
conda activate cppyy
```

## Build from the Source Code Repository

We are following a standard autoconf setup, which is a bit odd in the Python
world. You can build this library with the following:

```
git clone --recurse-submodules https://github.com/flatsurf/cppyythonizations.git
cd cppyythonizations
./bootstrap
./configure
make
make check # to run our test suite
make install # to install into /usr/local
```

Note that this is a pure Python library, so essentially all this does is setup
a `setup.py` file and run it.


## Build from the Source Code Repository with Conda Dependencies

To build this package, you need a fairly recent C++ compiler and probably some
packages that might not be readily available on your system. If you don't want
to use your distribution's packages, you can provide these dependencies with
conda. Download and install [Miniconda](https://conda.io/miniconda.html), then
run

```
conda config --add channels conda-forge
conda create -n cppyythonizations-build cppyy setuptools pytest
conda activate cppyythonizations-build
git clone --recurse-submodules https://github.com/flatsurf/cppyythonizations.git
cd cppyythonizations
./bootstrap
./configure --prefix="$CONDA_PREFIX"
make
```

## Build from the Source Code Repository with Conda

The conda recipe in `recipe/` is built automatically as part of our Continuous
Integration. If you want to build the recipe manually, something like the
following should work:

```
git clone --recurse-submodules https://github.com/flatsurf/cppyythonizations.git
cd cppyythonizations
conda activate root
conda config --add channels conda-forge
conda config --add channels flatsurf # if you want to pull in the latest version of dependencies
conda install conda-build conda-forge-ci-setup=2
export FEEDSTOCK_ROOT=`pwd`
export RECIPE_ROOT=${FEEDSTOCK_ROOT}/recipe
export CI_SUPPORT=${FEEDSTOCK_ROOT}/.ci_support
export CONFIG=linux_
make_build_number "${FEEDSTOCK_ROOT}" "${RECIPE_ROOT}" "${CI_SUPPORT}/${CONFIG}.yaml"
conda build "${RECIPE_ROOT}" -m "${CI_SUPPORT}/${CONFIG}.yaml" --clobber-file "${CI_SUPPORT}/clobber_${CONFIG}.yaml"
```

You can then try out the package that you just built with:
```
conda create -n cppyythonizations-test --use-local cppyythonizations
conda activate cppyythonizations-test
```

## Maintainers

* [@saraedum](https://github.com/saraedum)
* [@videlec](https://github.com/videlec)
