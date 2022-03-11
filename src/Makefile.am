## Build the python package in $(abs_builddir)/build
all-local:
	mkdir -p $(abs_builddir)/build
	cd $(abs_top_srcdir) && $(PYTHON) setup.py build --verbose --build-base $(abs_builddir)/build

## Install the python package we built above.
## Note that we cannot pass a --build-base here even though this invokes
## setuptools' build and egg_info steps which both write to the build
## directory. However, the default build directory is build/ relative to the
## current working directory and we built into that directory above so no
## build actually happens here anymore. (Which makes distcheck happy.)
install-exec-local:
	$(PYTHON) $(abs_top_srcdir)/setup.py install --prefix $(DESTDIR)$(prefix) --single-version-externally-managed --record $(DESTDIR)$(pythondir)/cppyythonizations/installed_files.txt --verbose

uninstall-local:
	cat $(DESTDIR)$(pythondir)/cppyythonizations/installed_files.txt | xargs rm -rf
	rm -rf $(DESTDIR)$(pythondir)/cppythonizations

clean-local:
	-rm -rf cppyythonizations/__pycache__ cppyythonizations.egg-info build .pytest_cache

EXTRA_DIST = cppyythonizations/__init__.py cppyythonizations/include cppyythonizations/pickling/__init__.py cppyythonizations/pickling/cereal.py cppyythonizations/pickling/cereal.hpp external/cereal/include/cereal cppyythonizations/util/__init__.py cppyythonizations/operators/__init__.py cppyythonizations/operators/order.py cppyythonizations/operators/arithmetic.py cppyythonizations/printing/__init__.py cppyythonizations/vector/__init__.py cppyythonizations/tuple/__init__.py
