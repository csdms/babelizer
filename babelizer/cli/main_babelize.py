#! /usr/bin/env python
import os
import pathlib
from collections import OrderedDict
from functools import partial

import click
import pkg_resources
import yaml
from scripting.contexts import cd
from scripting.unix import system

from .. import __version__
from ..errors import OutputDirExistsError, ValidationError
from ..metadata import PluginMetadata
from ..render import prettify_python, render, render_plugin_repo

out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)


class BabelizerAbort(click.Abort):
    def __init__(self, message):
        err(str(message))


@click.command()
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
def babelize(meta, output, template, quiet, verbose):
    template = template or pkg_resources.resource_filename("babelizer", "data")

    if not quiet:
        out(f"reading template from {template}")

    try:
        plugin_metadata = PluginMetadata.from_stream(meta)
        new_folder = render(plugin_metadata, output, template=template, clobber=False)
    except (ValidationError, OutputDirExistsError) as error:
        raise BabelizerAbort(error)

    if not quiet:
        out(
            "Don't forget to drop model metadata files into {0}".format(
                new_folder / "meta"
            )
        )

    print(new_folder)


@click.command()
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
def rebabelize(template, quiet, verbose):
    metadata_path = pathlib.Path("plugin.yaml").resolve()
    package_path = metadata_path.parent
    output_path = metadata_path.parent

    if not metadata_path.is_file():
        err("this does not appear to be a babelized folder (missing 'plugin.yaml')")
        raise click.Abort()

    template = template or pkg_resources.resource_filename("babelizer", "data")

    if not quiet:
        out(f"reading template from {template}")

    try:
        plugin_metadata = PluginMetadata.from_path(metadata_path)
    except ValidationError as error:
        raise BabelizerAbort(error)

    render(plugin_metadata, output_path, template=template, clobber=True)

    if not quiet:
        out(
            "Don't forget to drop model metadata files into {0}".format(
                package_path / "meta"
            )
        )

    print(package_path)


if __name__ == "__main__":
    babelize(auto_envvar_prefix="BABELIZE")
