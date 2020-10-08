#! /usr/bin/env python
import fnmatch
import os
import pathlib
import tempfile
from functools import partial

import click
import git
import pkg_resources

from .errors import OutputDirExistsError, ScanError, SetupPyError, ValidationError
from .metadata import BabelMetadata
from .render import render
from .utils import get_setup_py_version, save_files

out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)
# ask = partial(click.prompt, show_default=True, err=True)
yes = partial(click.confirm, show_default=True, err=True)


class BabelizerAbort(click.Abort):
    def __init__(self, message):
        err(str(message))


@click.group()
@click.version_option()
@click.option(
    "--cd",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    help="chage to directory, then execute",
)
def babelize(cd):
    os.chdir(cd)


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
@click.option(
    "--package-version",
    default="0.1",
    help="The initial version of the babelized package",
)
@click.argument("meta", type=click.File(mode="r"))
@click.argument(
    "output",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
)
def init(meta, output, template, quiet, verbose, package_version):
    template = template or pkg_resources.resource_filename("babelizer", "data")

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
            "Don't forget to drop model metadata files into {0}".format(
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
    package_path = pathlib.Path(".").resolve()

    for fname in ("babel.toml", "babel.yaml", "plugin.yaml"):
        if (package_path / fname).is_file():
            metadata_path = package_path / fname
            break
    else:
        metadata_path = None

    if not metadata_path:
        err("this does not appear to be a babelized folder (missing 'babel.yaml')")
        raise click.Abort()

    template = template or pkg_resources.resource_filename("babelizer", "data")

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
            "Don't forget to drop model metadata files into {0}".format(
                package_path / "meta"
            )
        )

    print(package_path)


@babelize.command()
@click.option(
    "--no-input",
    is_flag=True,
    help="Don’t ask questions, just use the default values",
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
@click.option("--requirement", help="Requirement", multiple=True, default=None)
@click.argument("file_", metavar="FILENAME", type=click.File(mode="w", lazy=True))
def generate(
    no_input,
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
    file_,
):
    """Generate babelizer config file, FILENAME."""

    meta = _gather_input(
        no_input=no_input,
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
    )

    print(BabelMetadata(**meta).format(fmt="toml"), file=file_)


def _gather_input(
    no_input=False,
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
):
    """Gather input either from command-line option, default, or user prompt.

    If a value is not ``None``, that means it was provided on the command
    line and so its value will be used. Otherwise, depending on
    the value of ``no_input``, either a default value is used or
    the user will be prompted for a value.
    """

    if no_input:

        def ask(text, default=None, **kwds):
            return default

    else:
        ask = partial(click.prompt, show_default=True, err=True)

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
        or ask("License to use for the babelized project", default="MIT"),
        "summary": summary
        or ask("Brief description of what the library does", default=""),
    }

    language = language or ask(
        "Programming language of the library being babelized",
        show_choices=["c", "c++", "fortran", "python"],
        default="c",
    )

    libraries = {}
    if no_input or any([x is not None for x in (name, library, header, entry_point)]):
        babelized_class = name or ask("Name of babelized class", default="<name>")
        libraries[babelized_class] = {
            "language": language,
            "library": library
            or ask(f"[{babelized_class}] Name of library to babelize", default=""),
            "header": header
            or ask(
                f"[{babelized_class}] Name of header file containing BMI class ",
                default="",
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
                "header": ask(
                    f"[{babelized_class}] Name of header file containing BMI class "
                ),
                "entry_point": ask(f"[{babelized_class}] Name of BMI class "),
            }
            if not yes("Add another library?", default=False):
                break

    return {"library": libraries, "package": package, "info": info, "build": {}}


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
