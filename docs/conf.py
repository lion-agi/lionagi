import os
import sys

# Insert your package directory so autodoc can find your modules
sys.path.insert(0, os.path.abspath(".."))

project = "LionAGI"
author = "Haiyang Li"
copyright = "2025"
release = "0.7"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "furo"
html_static_path = ["_static"]
html_title = "LionAGI Documentation"

html_theme_options = {
    "sidebar_hide_name": True,
    "navigation_with_keys": True,
    # Hide the “On This Page” panel:
    "light_css_variables": {
        "color-brand-primary": "#3070a0",
        "color-brand-content": "#3070a0",
        "font-size--body": "16px",
    },
    "dark_css_variables": {
        "color-brand-primary": "#5dafff",
        "color-brand-content": "#5dafff",
    },
}
pygments_style = "friendly"
pygments_dark_style = "solarized-dark"

html_css_files = [
    "custom.css",  # loads after theme CSS
]

# If you want a logo, place 'logo.png' in _static/
# html_logo = "_static/logo.png"

# Example: Add any additional Sphinx config below
# napoleon_use_param = True
# todo_include_todos = True
