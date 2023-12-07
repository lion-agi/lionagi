import os
import sys

sys.path.insert(0, os.path.abspath("../"))

with open("../lionagi/version.py") as v:
    exec(v.read())

# Configuration file for the Sphinx documentation builder.

# -- Project information
project = "lionagi"
copyright = "2023, Haiyang Li"
author = "Haiyang Li"

version = __version__
release = __version__

# -- General configuration
extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    "sphinx.ext.coverage",
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

templates_path = ["_templates"]

# -- Options for HTML output
html_title = project + " " + version
html_theme = 'sphinx_rtd_theme'


