"""Render a new babelized project."""

from __future__ import annotations

import datetime
import os
import sys
from typing import Any

import git

from babelizer.metadata import BabelMetadata

try:
    import black as blk
    import isort
except ModuleNotFoundError:
    MAKE_PRETTY = False
else:
    MAKE_PRETTY = True

if sys.version_info >= (3, 11):  # pragma: no cover (PY11+)
    import tomllib
else:  # pragma: no cover (<PY311)
    import tomli as tomllib

from babelizer._cookiecutter import cookiecutter
from babelizer._datadir import get_datadir
from babelizer._files.bmi_py import render as render_bmi
from babelizer._files.gitignore import render as render_gitignore
from babelizer._files.init_py import render as render_init
from babelizer._files.lib_init_py import render as render_lib_init
from babelizer._files.license_rst import render as render_license
from babelizer.errors import OutputDirExistsError
from babelizer.errors import RenderError


def render(
    plugin_metadata: BabelMetadata,
    output: str,
    template: str | None = None,
    clobber: bool = False,
    version: str = "0.1",
    make_pretty: bool = False,
) -> str:
    """Generate a babelized library.

    Parameters
    ----------
    plugin_metadata : BabelMetadata
        The metadata used to babelize the library.
    output : str
        Name of the directory that will be the new repository.
    template : str, optional
        Path (or URL) to the cookiecutter template to use.
    clobber : bool, optional
        If a like-named repository already exists, overwrite it.
    version : str, optional
        Version of babelized library.
    make_pretty : bool, optional
        If black and isort are available, run them over the generated project.

    Returns
    -------
    str
        Path to babelized library

    Raises
    ------
    OutputDirExistsError
        Raised if output directory exists and clobber is not set.
    """
    if template is None:
        template = get_datadir()

    context = {
        "files": {
            "_bmi.py": render_bmi(plugin_metadata),
            "__init__.py": render_init(plugin_metadata),
            "lib/__init__.py": render_lib_init(plugin_metadata),
            ".gitignore": render_gitignore(plugin_metadata),
            "LICENSE.rst": render_license(plugin_metadata),
        },
        "now": datetime.datetime.now(),
        "package_version": version,
    } | {k: plugin_metadata[k] for k in plugin_metadata}

    if os.path.exists(output):
        raise OutputDirExistsError(output)

    cookiecutter(
        template,
        extra_context=context,
        output_dir=output,
        no_input=True,
        overwrite_if_exists=clobber,
    )

    path = os.path.realpath(output)

    with open(os.path.join(path, "babel.toml"), "w") as fp:
        plugin_metadata.dump(fp, fmt="toml")

    git.Repo.init(path)

    return path


def blacken_file(filepath: str) -> None:
    """Format a Python file with ``black``.

    Parameters
    ----------
    filepath : str
        Path-like object to a Python file.
    """
    with open(filepath) as fp:
        try:
            new_contents = blk.format_file_contents(
                fp.read(), fast=True, mode=blk.FileMode()
            )
        except blk.NothingChanged:
            new_contents = None
    if new_contents:
        with open(filepath, "w") as fp:
            fp.write(new_contents)


def prettify_python(path_to_repo: str) -> None:
    """Format files in babelized project with ``black``.

    Parameters
    ----------
    path_to_repo : str
        Path-like object to babelized project.
    """
    with open(os.path.join(path_to_repo, "babel.toml")) as fp:
        meta = tomllib.loads(fp.read())
    module_name = meta["package"]["name"]

    files_to_fix = [
        os.path.join(path_to_repo, module_name, "_bmi.py"),
        os.path.join(path_to_repo, module_name, "__init__.py"),
        os.path.join(path_to_repo, "docs", "conf.py"),
    ]

    config = isort.Config(quiet=True)
    for file_to_fix in files_to_fix:
        isort.api.sort_file(file_to_fix, config=config)
        blacken_file(file_to_fix)
