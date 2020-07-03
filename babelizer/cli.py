#! /usr/bin/env python
import os
import pathlib
import sys
from functools import partial

import click
import pkg_resources

from .errors import OutputDirExistsError, ValidationError
from .metadata import BabelMetadata
from .render import render

out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)
ask = partial(click.prompt, show_default=True, err=True)


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
    "--template", default=None, help="Location of cookiecutter template",
)
@click.argument("meta", type=click.File(mode="r"))
@click.argument(
    "output",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
)
def init(meta, output, template, quiet, verbose):
    template = template or pkg_resources.resource_filename("babelizer", "data")

    if not quiet:
        out(f"reading template from {template}")

    try:
        babel_metadata = BabelMetadata.from_stream(meta)
        new_folder = render(babel_metadata, output, template=template, clobber=False)
    except (ValidationError, OutputDirExistsError) as error:
        raise BabelizerAbort(error)

    if not quiet:
        out(
            "Don't forget to drop model metadata files into {0}".format(
                new_folder / "meta"
            )
        )

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
    "--template", default=None, help="Location of cookiecutter template",
)
def update(template, quiet, verbose):
    package_path = pathlib.Path(".").resolve()

    for fname in ("babel.yaml", "plugin.yaml"):
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

    out(f"re-rendering {package_path}")
    render(babel_metadata, package_path.parent, template=template, clobber=True)

    if not quiet:
        out(
            "Don't forget to drop model metadata files into {0}".format(
                package_path / "meta"
            )
        )

    print(package_path)


@babelize.command()
@click.option(
    "--batch", is_flag=True, help="Run in batch mode using defaults for all values",
)
@click.option(
    "--name", help="Name to use for the babelized package",
)
@click.option(
    "--language",
    help="Programming language of the library being babelized",
    type=click.Choice(["c", "c++", "fortran", "python"], case_sensitive=False),
)
@click.option("--author", help="Babelizing author")
@click.option(
    "--username", help="GitHub username or organization that will host the project",
)
@click.option(
    "--license", help="License to use for the babelized project",
)
@click.option(
    "--summary", help="Brief description of what the library does",
)
@click.option(
    "--entry-point", help="Entry point to the library BMI", multiple=True, default=None
)
@click.option("--requirement", help="Requirement", multiple=True, default=None)
def quickstart(
    batch, name, language, author, username, license, summary, entry_point, requirement
):
    def ask_until_done(text):
        answers = []
        while (answer := ask(text, default="done")) != "done":
            answers.append(answer)
        return answers

    if batch:
        name = name or ""
        language = language or "c"
        author = author or "csdms"
        username = username or "pymt-lab"
        license = license or "MIT"
        summary = summary or ""
        entry_points = entry_point or ()
        requirements = requirement or ()
    else:
        name = name or ask("Name to use for the babelized package", default="")
        language = language or ask(
            "Programming language of the library being babelized",
            show_choices=["c", "c++", "fortran", "python"],
            default="c",
        )
        author = author or ask("Babelizing author", default="csdms")
        username = username or ask(
            "GitHub username or organization that will host the project",
            default="pymt-lab",
        )
        license = license or ask(
            "License to use for the babelized project", default="MIT"
        )
        summary = summary or ask(
            "Brief description of what the library does", default=""
        )

        entry_points = entry_point or ask_until_done("Entry point")
        requirements = requirement or ask_until_done("Requirement")

    print(
        BabelMetadata(
            library={"language": language, "entry_point": entry_points},
            plugin={"name": name, "requirements": requirements},
            info={
                "github_username": username,
                "plugin_author": author,
                "plugin_license": license,
                "summary": summary,
            },
            build={},
        ).format()
    )


if __name__ == "__main__":
    babelize(auto_envvar_prefix="BABELIZE")
