"""The command line interface to the babelizer."""

import fnmatch
import os
import pathlib
import sys
import tempfile
from functools import partial

import click
import git

if sys.version_info >= (3, 12):  # pragma: no cover (PY12+)
    import importlib.resources as importlib_resources
else:  # pragma: no cover (<PY312)
    import importlib_resources

from .errors import OutputDirExistsError
from .errors import ScanError
from .errors import SetupPyError
from .errors import ValidationError
from .metadata import BabelMetadata
from .render import render
from .utils import get_setup_py_version
from .utils import save_files

out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)
# ask = partial(click.prompt, show_default=True, err=True)
yes = partial(click.confirm, show_default=True, err=True)


class BabelizerAbort(click.Abort):
    """Exception raised when a user interrupts the babelizer."""

    def __init__(self, message):
        err(str(message))


@click.group()
@click.version_option()
@click.option(
    "--cd",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    help="Change to directory, then execute.",
)
def babelize(cd):
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
    help="Location of cookiecutter template",
)
@click.option(
    "--package-version",
    default="0.1",
    help="The initial version of the babelized package",
)
@click.argument("meta", type=click.File(mode="r"))
def init(meta, template, quiet, verbose, package_version):
    """Initialize a repository with babelized project files.

    META is babelizer configuration information, usually saved to a file.
    """
    output = pathlib.Path(".")
    template = template or str(importlib_resources.files("babelizer") / "data")

    if not quiet:
        out(f"reading template from {template}")

    fmt = pathlib.Path(meta.name).suffix[1:] or "toml"
    try:
        babel_metadata = BabelMetadata.from_stream(meta, fmt=fmt)
    except (ScanError, ValidationError) as error:
        raise BabelizerAbort(error)

    try:
        new_folder = render(
            babel_metadata,
            output,
            template=template,
            clobber=False,
            version=package_version,
        )
    except (ValidationError, OutputDirExistsError) as error:
        raise BabelizerAbort(error)

    if not quiet:
        out(
            "Don't forget to drop model metadata files into {}".format(
                new_folder / "meta"
            )
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
    help="Location of cookiecutter template",
)
def update(template, quiet, verbose):
    """Update an existing babelized project."""
    package_path = pathlib.Path(".").resolve()

    for fname in ("babel.toml", "babel.yaml", "plugin.yaml"):
        if (package_path / fname).is_file():
            metadata_path = package_path / fname
            break
    else:
        metadata_path = None

    if not metadata_path:
        err("this does not appear to be a babelized folder (missing 'babel.toml')")
        raise click.Abort()

    template = template or str(importlib_resources.files("babelizer") / "data")

    if not quiet:
        out(f"reading template from {template}")

    try:
        babel_metadata = BabelMetadata.from_path(metadata_path)
    except ValidationError as error:
        raise BabelizerAbort(error)

    try:
        version = get_setup_py_version()
    except SetupPyError as error:
        raise BabelizerAbort(
            os.linesep.join(["the setup.py of this package has an error:", f"{error}"])
        )

    out(f"re-rendering {package_path}")
    with save_files(["CHANGES.rst", "CREDITS.rst"]):
        render(
            babel_metadata,
            package_path.parent,
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
            "Don't forget to drop model metadata files into {}".format(
                package_path / "meta"
            )
        )

    print(package_path)


@babelize.command()
@click.option(
    "--prompt",
    is_flag=True,
    help="Prompt the user for values",
)
@click.option(
    "--package",
    help="Name to use for the babelized package",
)
@click.option(
    "--name",
    help="Name of the babelized class",
)
@click.option(
    "--email",
    help="Contact email to use for the babelized package",
)
@click.option(
    "--language",
    help="Programming language of the library being babelized",
    type=click.Choice(["c", "c++", "fortran", "python"], case_sensitive=False),
)
@click.option("--author", help="Babelizing author")
@click.option(
    "--username",
    help="GitHub username or organization that will host the project",
)
@click.option(
    "--license",
    help="License to use for the babelized project",
)
@click.option(
    "--summary",
    help="Brief description of what the library does",
)
@click.option("--library", help="Name of the BMI library to wrap", default=None)
@click.option(
    "--header", help="Name of the header file declaring the BMI class", default=None
)
@click.option(
    "--entry-point", help="Name of the BMI entry point into the library", default=None
)
@click.option("--requirement", help="Required libraries", multiple=True, default=None)
@click.option("--python-version", help="Supported Python versions", default="3.9")
@click.option(
    "--os-name", help="Supported operating systems", default="linux,mac,windows"
)
def generate(
    prompt,
    package,
    name,
    email,
    language,
    author,
    username,
    license,
    summary,
    library,
    header,
    entry_point,
    requirement,
    python_version,
    os_name,
):
    """Generate the babelizer configuration file."""
    meta = _gather_input(
        prompt=prompt,
        package=package,
        name=name,
        email=email,
        language=language,
        author=author,
        username=username,
        license=license,
        summary=summary,
        library=library,
        header=header,
        entry_point=entry_point,
        requirement=requirement,
        python_version=python_version,
        os_name=os_name,
    )

    print(BabelMetadata(**meta).format(fmt="toml"))


def _gather_input(
    prompt=False,
    package=None,
    name=None,
    email=None,
    language=None,
    author=None,
    username=None,
    license=None,
    summary=None,
    library=None,
    header=None,
    entry_point=None,
    requirement=None,
    python_version=None,
    os_name=None,
):
    """Gather input either from command-line option, default, or user prompt.

    If a value is not ``None``, that means it was provided on the command
    line and so its value will be used. Otherwise, depending on
    the value of ``no_input``, either a default value is used or
    the user will be prompted for a value.
    """
    if prompt:
        ask = partial(click.prompt, show_default=True, err=True)
    else:

        def ask(text, default=None, **kwds):
            return default

    def _split_if_str(val, sep=","):
        return val.split(sep) if isinstance(val, str) else val

    python_version = _split_if_str(python_version)
    os_name = _split_if_str(os_name)

    def ask_until_done(text):
        answers = []
        while (answer := ask(text, default="done")) != "done":
            answers.append(answer)
        return answers

    package = {
        "name": package or ask("Name to use for the babelized package", default=""),
        "requirements": requirement or ask_until_done("Requirement"),
    }
    info = {
        "github_username": username
        or ask(
            "GitHub username or organization that will host the project",
            default="pymt-lab",
        ),
        "package_author": author or ask("Babelizing author", default="csdms"),
        "package_author_email": email
        or ask("Babelizing author email", default="csdms@colorado.edu"),
        "package_license": license
        or ask("License to use for the babelized project", default="MIT License"),
        "summary": summary
        or ask("Brief description of what the library does", default=""),
    }

    language = language or ask(
        "Programming language of the library being babelized",
        show_choices=["c", "c++", "fortran", "python"],
        default="c",
    )

    ci = {
        "os": os_name
        or ask_until_done(
            "Supported operating system",
            show_choices=["linux", "mac", "windows", "all"],
            default="all",
        ),
        "python_version": python_version
        or ask_until_done(
            "Supported python version",
            show_choices=["3.7", "3.8", "3.9"],
            default="3.9",
        ),
    }

    libraries = {}
    if (not prompt) or any(x is not None for x in (name, library, header, entry_point)):
        babelized_class = name or ask("Name of babelized class", default="<name>")
        libraries[babelized_class] = {
            "language": language,
            "library": library
            or ask(f"[{babelized_class}] Name of library to babelize", default=""),
            "header": header
            or (
                ask(
                    f"[{babelized_class}] Name of header file containing BMI class ",
                    default="",
                )
                if language != "python"
                else "__UNUSED__"
            ),
            "entry_point": entry_point
            or ask(f"[{babelized_class}] Name of BMI class ", default=""),
        }
    else:
        while 1:
            babelized_class = ask("Name of babelized class")
            libraries[babelized_class] = {
                "language": language,
                "library": ask(f"[{babelized_class}] Name of library to babelize"),
                "header": (
                    ask(
                        f"[{babelized_class}] Name of header file containing BMI class "
                    )
                    if language != "python"
                    else "__UNUSED__"
                ),
                "entry_point": ask(f"[{babelized_class}] Name of BMI class "),
            }
            if not yes("Add another library?", default=False):
                break

    return {
        "library": libraries,
        "package": package,
        "info": info,
        "build": {},
        "ci": ci,
    }


def _get_dir_contents(base, trunk=None):
    base = pathlib.Path(base)
    files = set()
    for item in base.iterdir():
        if item.is_dir():
            files |= _get_dir_contents(item, trunk=trunk)
        else:
            files.add(str(item.relative_to(trunk)))

    return files


def _repo_contents(base):
    repo = git.Repo(str(base))
    return set(
        repo.git.ls_tree("--full-tree", "-r", "--name-only", "HEAD").splitlines()
    )


def _generated_files(babel_metadata, template=None, version="0.1"):
    with tempfile.TemporaryDirectory() as tmpdir:
        new_folder = render(
            babel_metadata,
            tmpdir,
            template=template,
            version=version,
        )
        return _get_dir_contents(new_folder, trunk=new_folder)


if __name__ == "__main__":
    babelize(auto_envvar_prefix="BABELIZE")
