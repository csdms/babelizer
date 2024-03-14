"""Render a new babelized project."""

import contextlib
import os
import pathlib
import sys

import git
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

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
if sys.version_info >= (3, 12):  # pragma: no cover (PY12+)
    import importlib.resources as importlib_resources
else:  # pragma: no cover (<PY312)
    import importlib_resources

from babelizer._files.bmi_py import render as render_bmi
from babelizer._files.gitignore import render as render_gitignore
from babelizer._files.init_py import render as render_init
from babelizer._files.lib_init_py import render as render_lib_init
from babelizer._files.license_rst import render as render_license
from babelizer.errors import OutputDirExistsError
from babelizer.errors import RenderError


def render(
    plugin_metadata,
    output,
    template=None,
    clobber=False,
    version="0.1",
    make_pretty=False,
):
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
        template = str(importlib_resources.files("babelizer") / "data")

    context = plugin_metadata.as_cookiecutter_context()
    context["files"] = {
        "_bmi.py": render_bmi(plugin_metadata),
        "__init__.py": render_init(plugin_metadata),
        "lib/__init__.py": render_lib_init(plugin_metadata),
        ".gitignore": render_gitignore(plugin_metadata),
        "LICENSE.rst": render_license(plugin_metadata),
    }

    try:
        path = render_plugin_repo(
            template,
            context=dict(context, package_version=version),
            output_dir=output,
            clobber=clobber,
        )
    except OutputDirExistsException as err:
        raise OutputDirExistsError(", ".join(err.args))

    with open(path / "babel.toml", "w") as fp:
        plugin_metadata.dump(fp, fmt="toml")

    if make_pretty and MAKE_PRETTY:
        prettify_python(path)

    return path.resolve()


def render_plugin_repo(template, context=None, output_dir=".", clobber=False):
    """Render a repository for a pymt plugin.

    Parameters
    ----------
    template: str
        Path (or URL) to the cookiecutter template to use.
    context: dict, optional
        Context for the new repository.
    output_dir : str, optional
        Name of the directory that will be the new repository.
    clobber: bool, optional
        If a like-named repository already exists, overwrite it.

    Returns
    -------
    path
        Absolute path to the newly-created repository.
    """
    output_dir = pathlib.Path(output_dir)
    context = context or {}

    try:
        cookiecutter(
            template,
            extra_context=context,
            output_dir=output_dir,
            no_input=True,
            overwrite_if_exists=clobber,
        )
    except OutputDirExistsException as err:
        raise OutputDirExistsError(", ".join(err.args))

    name = context["package_name"]

    # path = os.path.join(output_dir, "{}".format(context["package_name"]))
    # if not os.path.isdir(path):
    path = output_dir / f"{name}"
    if not path.is_dir():
        raise RenderError(f"error creating {path}")

    git.Repo.init(path)

    return path


@contextlib.contextmanager
def as_cwd(path):
    """Change directory context.

    Parameters
    ----------
    path : str
        Path-like object to a directory.
    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)


def blacken_file(filepath):
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


def prettify_python(path_to_repo):
    """Format files in babelized project with ``black``.

    Parameters
    ----------
    path_to_repo : str
        Path-like object to babelized project.
    """
    path_to_repo = pathlib.Path(path_to_repo)
    with open(path_to_repo / "babel.toml") as fp:
        meta = tomllib.loads(fp.read())
    module_name = meta["package"]["name"]

    files_to_fix = [
        path_to_repo / "setup.py",
        path_to_repo / "setup_utils.py",
        path_to_repo / module_name / "_bmi.py",
        path_to_repo / module_name / "__init__.py",
        path_to_repo / "docs" / "conf.py",
    ]

    config = isort.Config(quiet=True)
    for file_to_fix in files_to_fix:
        isort.api.sort_file(file_to_fix, config=config)
        blacken_file(file_to_fix)
