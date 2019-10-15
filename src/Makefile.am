all-local:
	mkdir -p $(builddir)/build
	cd $(srcdir) && $(PYTHON) $(abs_top_builddir)/src/setup.py build --verbose --build-base $(abs_top_builddir)/src/build

install-exec-local:
	$(PYTHON) setup.py install --prefix $(DESTDIR)$(prefix) --single-version-externally-managed --record $(DESTDIR)$(pythondir)/cppyythonizations/install_files.txt --verbose

uninstall-local:
	cat $(DESTDIR)$(pythondir)/cppyythonizations/install_files.txt | xargs rm -rf
	rm -rf $(DESTDIR)$(pythondir)/cppyythonizations

clean-local:
	-rm -rf cppyythonizations/__pycache__ cppyythonizations.egg-info build .pytest_cache

BUILT_SOURCES = setup.py MANIFEST.in
EXTRA_DIST = setup.py.in MANIFEST.in.in cppyythonizations/__init__.py cppyythonizations/include cppyythonizations/pickle/cereal.py cppyythonizations/pickle/cereal.hpp
CLEANFILES = setup.py MANIFEST.in
$(builddir)/setup.py: $(srcdir)/setup.py.in Makefile
	sed -e 's,[@]abs_top_srcdir[@],$(abs_top_srcdir),g' -e 's,[@]PACKAGE_VERSION[@],$(PACKAGE_VERSION),g' < $< > $@
$(builddir)/MANIFEST.in: $(srcdir)/MANIFEST.in.in Makefile
	sed -e 's,[@]srcdir[@],$(srcdir),g' < $< > $@
