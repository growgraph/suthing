# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

from pkg_resources import get_distribution

project = "suthing"
copyright = "2025, Alexander Belikov"
author = "Alexander Belikov"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # For Google and NumPy-style docstrings
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = []

add_module_names = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]


sys.path.insert(0, os.path.abspath("../../suthing/"))

# Dynamically retrieve the version
project_version = get_distribution(
    "suthing"
).version  # Replace "suthing" with your project name
release = project_version  # Full version string
version = ".".join(project_version.split(".")[:2])  # Short version (e.g., "1.2")


rst_prolog = """
.. |release| replace:: {release}
.. |version| replace:: {version}
""".format(release=release, version=version)
