# conf.py — Sphinx configuration for your docs

import os
import sys

# Insert the path to your main package so autodoc can find it
# (Adjust the relative path to match your repo's layout)
sys.path.insert(0, os.path.abspath(".."))

project = "LionAGI"
author = "Haiyang Li"
copyright = "2025"
release = "0.6"  # or version from your package

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # Google/NumPy style docstrings
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    # "sphinx.ext.autosummary",  # optional
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output ----------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "sidebar_hide_name": True,
    "navigation_with_keys": True,
    # Hide the “On This Page” panel if you want to rely solely on your local TOC
    "hide_pages_index": True,
    "light_css_variables": {
        "color-brand-primary": "#007ACC",
        "color-brand-content": "#006699",
    },
    "dark_css_variables": {
        "color-brand-primary": "#4DC1FF",
        "color-brand-content": "#99C2FF",
    },
}

# Tells Sphinx to include custom.css after the theme's CSS
html_css_files = [
    "custom.css",
]

# (Optional) a custom title for the entire site:
html_title = "LionAGI Documentation"


# -- Custom / Additional config options -----------------------------------
# e.g., napoleon_use_param = True
# or todo_include_todos = True
