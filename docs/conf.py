import os
import sys

sys.path.insert(0, os.path.abspath("../"))

with open("../lionagi/version.py") as v:
    exec(v.read(), globals())

global_version = globals().get("__version__")
if global_version is None:
    raise RuntimeError("Version could not be read from lionagi/version.py")

# Configuration file for the Sphinx documentation builder.

# -- Project information
project = "lionagi"
copyright = "2023, Haiyang Li"
author = "Haiyang Li"

version = global_version
release = global_version

# -- General configuration
extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    "sphinx.ext.coverage",
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
    'nbsphinx',
]
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}

intersphinx_disabled_domains = ['std']

templates_path = ["_templates"]

# -- Options for HTML output
html_title = project + " " + version
html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
