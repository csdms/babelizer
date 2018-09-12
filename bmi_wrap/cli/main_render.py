#! /usr/bin/env python
import os

import click
import yaml
from cookiecutter.main import cookiecutter
from scripting.contexts import cd
from scripting.unix import system

from .. import __version__


@click.command()
@click.version_option(version=__version__)
@click.option("--compile", is_flag=True, help="compile the extension module")
@click.option("--clobber", is_flag=True, help="clobber folder if it already exists")
@click.option(
    "--template",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
    help="Location of cookiecutter template",
)
@click.argument("meta", type=click.File(mode="r"))
@click.argument(
    "output",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
)
def main(meta, output, compile, clobber, template):

    config = yaml.load(meta)

    cookiecutter_config = {
        "full_name": config["info"]["plugin_author"],
        "github_username": config["info"]["github_username"],
        "module_name": config["pymt"]["module_name"],
        "bmi_include": config["library"]["bmi_include"],
        "bmi_register": config["library"]["entry_point"],
        "class_name": config["pymt"]["class_name"],
        "language": config["library"]["language"],
        "undef_macros": ",".join(config["build"]["undef_macros"]),
        "define_macros": ",".join(config["build"]["define_macros"]),
        "libraries": ",".join(config["build"]["libraries"]),
        "library_dirs": ",".join(config["build"]["library_dirs"]),
        "include_dirs": ",".join(config["build"]["include_dirs"]),
        "extra_compile_args": ",".join(config["build"]["extra_compile_args"]),
        "open_source_license": config["info"]["plugin_license"],
        "project_short_description": config["info"]["summary"],
    }

    cookiecutter(
        template,
        extra_context=cookiecutter_config,
        output_dir=output,
        no_input=True,
        overwrite_if_exists=clobber,
    )

    path = os.path.join(output, "pymt_{}".format(config["pymt"]["module_name"]))
    click.secho("Your pymt plugin can be found at {}".format(path), fg="green")

    if compile:
        with cd(path):
            system(["versioneer", "install"])
            system(["python", "setup.py", "develop"])
    else:
        click.secho("Build with:", fg="white")
        click.secho("    $ cd {0}".format(path), fg="white")
        click.secho("    $ versioneer install", fg="white")
        click.secho("    $ python setup.py develop", fg="white")


if __name__ == "__main__":
    main(auto_envvar_prefix="BMI_WRAP")
