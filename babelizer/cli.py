"""The command line interface to the babelizer."""

from __future__ import annotations

import fnmatch
import io
import os
import pathlib
import tempfile
from collections.abc import Collection
from functools import partial
from typing import cast

import click
import git

from babelizer._datadir import get_datadir
from babelizer._files.gitignore import render as render_gitignore
from babelizer._files.license_rst import render as render_license
from babelizer._files.meson_build import render as render_meson_build
from babelizer._files.readme import render as render_readme
from babelizer.errors import OutputDirExistsError
from babelizer.errors import ScanError
from babelizer.errors import SetupPyError
from babelizer.errors import ValidationError
from babelizer.metadata import BabelMetadata
from babelizer.render import render
from babelizer.utils import get_setup_py_version
from babelizer.utils import save_files

out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)


class BabelizerAbort(click.Abort):
    """Exception raised when a user interrupts the babelizer."""

    def __init__(self, message: str):
        err(message)


@click.group()
@click.version_option()
@click.option(
    "--cd",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    help="Change to directory, then execute.",
)
def babelize(cd: str) -> None:
    """Wrap BMI libraries with Python bindings."""
    os.chdir(cd)


@babelize.command()
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help=(
        "Don't emit non-error messages to stderr. Errors are still emitted, "
        "silence those with 2>/dev/null"
    ),
)
@click.option(
    "-v", "--verbose", is_flag=True, help="Also emit status messages to stderr"
)
@click.option(
    "--template",
    default=None,
    help="Location of templates",
)
@click.option(
    "--package-version",
    default="0.1",
    help="The initial version of the babelized package",
)
@click.argument("meta", type=click.File(mode="r"))
def init(
    meta: click.File, template: str, quiet: bool, verbose: bool, package_version: str
) -> None:
    """Initialize a repository with babelized project files.

    META is babelizer configuration information, usually saved to a file.
    """
    template = template or os.path.join(get_datadir(), "templates")

    if not quiet:
        out(f"reading template from {template}")

    fmt = pathlib.Path(meta.name).suffix[1:] or "toml"
    try:
        babel_metadata = BabelMetadata.from_stream(cast(io.TextIOBase, meta), fmt=fmt)
    except (ScanError, ValidationError) as error:
        raise BabelizerAbort(str(error))

    output = babel_metadata["package"]["name"]

    try:
        new_folder = render(
            babel_metadata,
            output,
            template=template,
            clobber=False,
            version=package_version,
        )
    except (ValidationError, OutputDirExistsError) as error:
        raise BabelizerAbort(str(error))

    if not quiet:
        out(
            "Don't forget to drop model metadata files into"
            f" {os.path.join(new_folder, 'meta')}"
        )

    repo = git.Repo(new_folder)
    repo.git.add("--all")
    repo.index.commit("Initial commit")

    print(new_folder)


@babelize.command()
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help=(
        "Don't emit non-error messages to stderr. Errors are still emitted, "
        "silence those with 2>/dev/null."
    ),
)
@click.option(
    "-v", "--verbose", is_flag=True, help="Also emit status messages to stderr."
)
@click.option(
    "--template",
    default=None,
    help="Location of templates",
)
@click.option(
    "--set-version", default=None, help="Set the version of the updated package"
)
def update(
    template: str | None, quiet: bool, verbose: bool, set_version: str | None
) -> None:
    """Update an existing babelized project."""

    package_path = os.path.realpath(".")
    for fname in ("babel.toml", "babel.yaml", "plugin.yaml"):
        # if (package_path / fname).is_file():
        #     metadata_path = package_path / fname
        if os.path.isfile(os.path.join(package_path, fname)):
            metadata_path = os.path.join(package_path, fname)
            break
    else:
        metadata_path = None

    if not metadata_path:
        err("this does not appear to be a babelized folder (missing 'babel.toml')")
        raise click.Abort()

    template = template or get_datadir()

    if not quiet:
        out(f"reading template from {template}")

    try:
        babel_metadata = BabelMetadata.from_path(metadata_path)
    except ValidationError as error:
        raise BabelizerAbort(str(error))

    try:
        version = set_version or get_setup_py_version()
    except SetupPyError as error:
        raise BabelizerAbort(
            os.linesep.join(
                [
                    "the setup.py of this package has an error:",
                    f"{error}"
                    "unable to get package's version. Try using the '--set-version' option",
                ]
            )
        )
    version = "0.1.0" if version is None else version

    out(f"re-rendering {package_path}")
    with save_files(["CHANGES.rst", "CREDITS.rst"]):
        render(
            babel_metadata,
            os.path.dirname(package_path),
            # package_path.parent,
            template=template,
            clobber=True,
            version=version,
        )

    extra_files = _repo_contents(package_path) - _generated_files(
        babel_metadata, template=template, version=version
    )

    ignore = ["meta*", "notebooks*", "docs*", "**/data"]
    for pattern in ignore:
        extra_files.difference_update(fnmatch.filter(extra_files, pattern))

    if extra_files:
        out(f"found extra files in {package_path}:")
        for name in sorted(extra_files):
            out(f"  {name}")

    if not quiet:
        out(
            "Don't forget to drop model metadata files into"
            f" {os.path.join(package_path, 'meta')}"
        )

    print(package_path)


@babelize.command()
def sample_config() -> None:
    """Generate the babelizer configuration file."""
    print_sample_config()


@babelize.command()
def sample_license() -> None:
    """Generate a license file."""
    context = {
        "info": {
            "package_author": "Lyle Lanley",
            "summary": "A Monorail!",
            "package_license": "MIT License",
        }
    }
    print(render_license(context))


@babelize.command()
def sample_gitignore() -> None:
    """Generate a .gitignore file."""
    context = {
        "package": {"name": "springfield_monorail"},
        "library": {"monorail": {"language": "c"}},
    }
    print(render_gitignore(context))


@babelize.command()
@click.argument("extension", nargs=-1)
def sample_meson_build(extension: Collection[str]) -> None:
    """Generate a meson.build file."""
    if len(extension) == 0:
        contents = render_meson_build(
            [
                "springfield_monorail/lib/monorail.pyx",
                "springfield_monorail/lib/rail.pyx",
            ],
            install=[
                "springfield_monorail/__init__.py",
                "springfield_monorail/_bmi.py",
                "springfield_monorail/_version.py",
                "springfield_monorail/lib/__init__.py",
                "springfield_monorail/lib/monorail.pyx",
                "springfield_monorail/lib/rail.pyx",
            ],
        )
    else:
        contents = render_meson_build(extension)

    print(contents)


@babelize.command()
def sample_readme() -> None:
    context = {
        "language": "python",
        "open_source_license": "MIT License",
        "package_name": "springfield_monorail",
        "info": {
            "github_username": "lyle-lanley",
            "package_author": "Lyle Lanley",
            "summary": "A Monorail!",
            "package_license": "MIT License",
        },
        "components": {
            "Monorail": {"library": "monorail"},
            "Rail": {"library": "rail"},
        },
    }
    print(render_readme(context))


def _get_dir_contents(base: str, trunk: str | None = None) -> set[str]:
    files = set()
    for item in os.listdir(base):
        if os.path.isdir(item):
            files |= _get_dir_contents(item, trunk=trunk)
        else:
            files.add(os.path.relpath(item, start=trunk))

    return files


def _repo_contents(base: str) -> set[str]:
    repo = git.Repo(base)
    return set(
        repo.git.ls_tree("--full-tree", "-r", "--name-only", "HEAD").splitlines()
    )


def _generated_files(
    babel_metadata: BabelMetadata, template: str | None = None, version: str = "0.1"
) -> set[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        new_folder = render(
            babel_metadata,
            tmpdir,
            template=template,
            version=version,
        )
        return _get_dir_contents(new_folder, trunk=new_folder)


SAMPLE_CONFIG = """\
# See https://babelizer.readthedocs.io/ for more information

# Describe the library being wrapped.
[library.Monorail]
language = "c"
library = "bmimonorail"
header = "monorail.h"
entry_point = "register_monorail"

# Describe compiler options need to build the library being
# wrapped.
[build]
undef_macros = []
define_macros = []
libraries = []
library_dirs = []
include_dirs = []
extra_compile_args = []

# Describe the newly wrapped package.
[package]
name = "springfield_monorail"
requirements = ["three_million_dollars"]

[info]
github_username = "lyle-lanley"
package_author = "Lyle Lanley"
package_author_email = "lyle@monorail.com"
package_license = "MIT License"
summary = '''
Well, sir, there's nothing on Earth like a genuine,
bona fide, electrified, six-car monorail. What'd I say?
Monorail! What's it called? Monorail! That's right! Monorail!
'''

[ci]
python_version = [
    "3.10",
    "3.11",
    "3.12",
]
os = [
    "linux",
    "mac",
    "windows",
]
"""


def print_sample_config() -> int:
    """Print a sample babelizer configuration file."""
    print(SAMPLE_CONFIG, end="")
    return 0


if __name__ == "__main__":
    babelize(auto_envvar_prefix="BABELIZE")
