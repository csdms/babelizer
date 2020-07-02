#! /usr/bin/env python
import os
import pathlib
from functools import partial

import click
import pkg_resources

from .. import __version__
from ..errors import OutputDirExistsError, ValidationError
from ..metadata import BabelMetadata
from ..render import render

out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)


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
@click.version_option(version=__version__)
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
@click.version_option(version=__version__)
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


if __name__ == "__main__":
    babelize(auto_envvar_prefix="BABELIZE")
