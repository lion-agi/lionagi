SHELL = /bin/sh

SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

.PHONY: help clean html livehtml

help:
	@echo "Please use 'make <target>' where <target> is one of:"
	@echo "  html       to build the HTML documentation"
	@echo "  clean      to remove build artifacts"
	@echo "  livehtml   to run autobuild for live reloading"

clean:
	rm -rf $(BUILDDIR)/*

html:
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)"

# Optional: live reload docs as you edit
livehtml:
	sphinx-autobuild $(SOURCEDIR) $(BUILDDIR)/html --port 8000
