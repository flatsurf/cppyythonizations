A collection of [Pythonizations](https://cppyy.readthedocs.io/en/latest/pythonizations.html) for [cppyy](https://cppyy.readthedocs.io/en/latest/index.html).

These mostly work around known limitations of cppyy or provide some
reusable extensions such as Python pickling of C++ classes.

## Install with Conda

You can install this package with conda. Download and install [Miniconda](https://conda.io/miniconda.html), then run

```
conda config --add channels conda-forge
conda create -n cppyy -c flatsurf cppyy cppyythonizations
conda activate cppyy
```

## Install with pip

```
pip install cppyythonizations
```

## Maintainers

* [@saraedum](https://github.com/saraedum)
* [@videlec](https://github.com/videlec)
