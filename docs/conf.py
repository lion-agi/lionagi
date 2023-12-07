from ..version import __version__

ver = __version__

# Configuration file for the Sphinx documentation builder.

# -- Project information
project = "lionagi"
copyright = "2023, Haiyang Li"
author = "Haiyang Li"

version = ver
release = ver

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


