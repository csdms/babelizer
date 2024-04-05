"""Render a new babelized project."""

from __future__ import annotations

import datetime
import os

import git

from babelizer._cookiecutter import cookiecutter
from babelizer._datadir import get_template_dir
from babelizer._files.bmi_py import render as render_bmi
from babelizer._files.gitignore import render as render_gitignore
from babelizer._files.init_py import render as render_init
from babelizer._files.lib_init_py import render as render_lib_init
from babelizer._files.license_rst import render as render_license
from babelizer.config import BabelConfig
from babelizer.errors import OutputDirExistsError


def render(
    babel_config: BabelConfig,
    output: str,
    template: str | None = None,
    clobber: bool = False,
    version: str = "0.1",
    make_pretty: bool = False,
) -> str:
    """Generate a babelized library.

    Parameters
    ----------
    babel_config : BabelConfig
        The configuration used to babelize the library.
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
        template = get_template_dir()

    context = {
        "files": {
            "_bmi.py": render_bmi(babel_config),
            "__init__.py": render_init(babel_config),
            "lib/__init__.py": render_lib_init(babel_config),
            ".gitignore": render_gitignore(babel_config),
            "LICENSE.rst": render_license(babel_config),
        },
        "now": datetime.datetime.now(),
        "package_version": version,
    } | {k: babel_config[k] for k in babel_config}

    if os.path.exists(output):
        raise OutputDirExistsError(output)

    cookiecutter(template, context=context, output_dir=output)

    path = os.path.realpath(output)

    with open(os.path.join(path, "babel.toml"), "w") as fp:
        babel_config.dump(fp, fmt="toml")

    git.Repo.init(path)

    return path
