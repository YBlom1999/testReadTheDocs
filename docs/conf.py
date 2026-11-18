# Configuration file for the Sphinx documentation builder.
# Full list of options: https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = "My Project"
author = "Your Name"
copyright = "2026, Your Name"
release = "0.1.0"  # full version, e.g. "1.2.3"
version = "0.1"  # short X.Y version

# -- General configuration ---------------------------------------------------

extensions = [
    # "sphinx.ext.autodoc",       # pull docstrings from your code
    # "sphinx.ext.napoleon",      # Google/NumPy style docstrings
    # "sphinx.ext.viewcode",      # links to highlighted source
    # "sphinx.ext.intersphinx",   # link to other projects' docs
    # "myst_parser",              # write docs in Markdown (pip install myst-parser)
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Uncomment if you use myst_parser and want both .rst and .md files:
# source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# Uncomment if you use autodoc and your package lives in ../src or ../:
# import os, sys
# sys.path.insert(0, os.path.abspath("../src"))

# intersphinx_mapping = {
#     "python": ("https://docs.python.org/3", None),
# }

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"  # requires sphinx-rtd-theme in docs/requirements.txt
# html_static_path = ["_static"]  # create docs/_static/ before enabling
# html_logo = "_static/logo.png"
# html_title = project

# -- Read the Docs -----------------------------------------------------------
# RTD injects its own settings during builds; nothing extra is required here.
