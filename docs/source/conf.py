# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import datetime
import os
import pathlib
import sys

from babelizer._version import __version__

# -- Path setup --------------------------------------------------------------


sys.path.insert(0, os.path.abspath("../.."))
docs_dir = os.path.dirname(__file__)


# The master toctree document.
master_doc = "index"

# -- Project information -----------------------------------------------------

project = "babelizer"
author = "Community Surface Dynamics Modeling System"
version = __version__
release = version
this_year = datetime.date.today().year
copyright = f"{this_year}, {author}"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx_inline_tabs",
    "sphinx_click",
    "sphinx_copybutton",
    "sphinxcontrib.towncrier",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: list[str] = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"
# html_theme = "furo"
html_title = "babelizer"
language = "en"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "_static/powered-by-logo-header.png"

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
    "index": [
        "sidebarintro.html",
        "links.html",
        "sourcelink.html",
        "searchbox.html",
    ],
    "**": [
        "sidebarintro.html",
        "links.html",
        "sourcelink.html",
        "searchbox.html",
    ],
}

# html_theme_options = {
#     "announcement": None,
#     "source_repository": "https://github.com/csdms/babelizer/",
#     "source_branch": "develop",
#     "source_directory": "docs/source",
#     "sidebar_hide_name": False,
#     "footer_icons": [
#         {
#             "name": "power",
#             "url": "https://csdms.colorado.edu",
#             "html": """
#                <svg stroke="currentColor" fill="currentColor" stroke-width="0" version="1.1" viewBox="0 0 16 16" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M6 0l-6 8h6l-4 8 14-10h-8l6-6z"></path></svg>
#                <b><i>Powered by CSDMS</i></b>
#             """,
#             "class": "",
#         },
#     ],
# }
# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}


# -- Options for towncrier_draft extension --------------------------------------------

towncrier_draft_autoversion_mode = "draft"  # or: 'sphinx-release', 'sphinx-version'
towncrier_draft_include_empty = True
towncrier_draft_working_directory = pathlib.Path(docs_dir).parent.parent

autodoc_default_options = {"special-members": "__init__", "undoc-members": True}
