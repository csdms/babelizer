#! /usr/bin/env python
import os
from collections import OrderedDict
from functools import partial

import click
import pkg_resources
from scripting.contexts import cd
from scripting.unix import system

from .. import __version__
from ..metadata import PluginMetadata
from ..render import prettify_python, render_plugin_repo

out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)


@click.command()
@click.version_option(version=__version__)
@click.option("--clobber", is_flag=True, help="clobber folder if it already exists")
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
def babelize(meta, output, clobber, template, quiet, verbose):

    config = PluginMetadata(meta)

    template = template or pkg_resources.resource_filename("babelizer", "data")

    if not quiet:
        out(f"reading template from {template}")

    path = render_plugin_repo(
        template,
        context=config.as_cookiecutter_context(),
        output_dir=output,
        clobber=clobber,
    )

    with open(os.path.join(path, "plugin.yaml"), "w") as fp:
        config.dump(fp)

    prettify_python(path)

    if not quiet:
        out(f"Your pymt plugin can be found at {path}")

    out("Checklist of things to do:")
    checklist = OrderedDict(
        [
            ("versioneer install", " "),
            ("make lint", " "),
            ("make docs", " "),
        ]
    )
    if not quiet:
        for item, status in checklist.items():
            out(f"[{status}] {item}")

    if not quiet:
        out(
            "Don't forget to drop model metadata files into {0}".format(
                os.path.join(path, "meta")
            )
        )


if __name__ == "__main__":
    babelize(auto_envvar_prefix="BABELIZE")
