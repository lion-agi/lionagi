# Makefile — On Linux/macOS, run "make html" or "make latexpdf"

SHELL = /bin/sh

SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

.PHONY: help clean html

help:
	@echo "Please use 'make <target>' where <target> is one of:"
	@echo "  html   to build the HTML documentation"
	@echo "  clean  to remove build artifacts"

clean:
	rm -rf $(BUILDDIR)/*

html:
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)"
