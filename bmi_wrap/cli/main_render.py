#! /usr/bin/env python
import os
import re
from collections import OrderedDict

import click
import six
import yaml
from cookiecutter.main import cookiecutter

from scripting.contexts import cd
from scripting.unix import system

from .. import __version__


_TEMPLATE_URI = "http://github.com/mcflugen/cookiecutter-bmi-wrap"


def setup_yaml_with_canonical_dict():
    """ https://stackoverflow.com/a/8661021 """
    yaml.add_representer(
        OrderedDict,
        lambda self, data: self.represent_mapping(
            "tag:yaml.org,2002:map", data.items()
        ),
        Dumper=yaml.SafeDumper,
    )

    def repr_ordered_dict(self, data):
        return self.represent_mapping("tag:yaml.org,2002:map", data.items())

    yaml.add_representer(dict, repr_ordered_dict, Dumper=yaml.SafeDumper)

    def repr_dict(self, data):
        return self.represent_mapping(
            "tag:yaml.org,2002:map", sorted(data.items(), key=lambda t: t[0])
        )

    yaml.add_representer(dict, repr_dict, Dumper=yaml.SafeDumper)

    # https://stackoverflow.com/a/45004464
    def repr_str(dumper, data):
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_str(data)

    yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)

    def repr_tuple(dumper, data):
        return dumper.represent_sequence("tag:yaml.org,2002:seq", list(data))

    yaml.add_representer(tuple, repr_tuple, Dumper=yaml.SafeDumper)

    # loader = yaml.SafeLoader
    yaml.add_implicit_resolver(
        u"tag:yaml.org,2002:float",
        re.compile(
            u"""^(?:
         [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
        |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
        |\\.[0-9_]+(?:[eE][-+][0-9]+)?
        |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
        |[-+]?\\.(?:inf|Inf|INF)
        |\\.(?:nan|NaN|NAN))$""",
            re.X,
        ),
        list(u"-+0123456789."),
    )


setup_yaml_with_canonical_dict()


class BmiWrapError(Exception):
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message


class ValidationError(BmiWrapError):

    pass


class RenderError(BmiWrapError):

    pass


def validate_meta(meta):
    missing_sections = set(PluginMetadata.REQUIRED) - set(meta)
    if missing_sections:
        raise ValidationError(
            "missing required sections {0}".format(", ".join(missing_sections))
        )

    for section, values in PluginMetadata.REQUIRED.items():
        missing_values = set(values) - set(meta[section])
        if missing_values:
            raise ValidationError(
                "missing required values {0}".format(", ".join(missing_values))
            )

    def _is_iterable_of_strings(value):
        if isinstance(value, six.string_types):
            return False
        for item in value:
            if not isinstance(item, six.string_types):
                return False
        return True

    for key, value in meta["build"].items():
        if not _is_iterable_of_strings(value):
            raise ValidationError("not an iterable of strings: build->{0}".format(key))

    for value in meta["build"]["define_macros"]:
        if len(value.split("=")) != 2:
            raise ValidationError(
                "build->define_macros must be of the form 'key=value'"
            )


class PluginMetadata(object):
    REQUIRED = {
        "library": ("name", "language", "entry_point"),
        "plugin": ("name", "module", "class", "conda_package"),
        "info": ("plugin_author", "github_username", "plugin_license", "summary"),
    }

    def __init__(self, filepath):
        self._meta = PluginMetadata.norm(yaml.load(filepath))
        validate_meta(self._meta)

    def get(self, section, value):
        return self._meta[section][value]

    @staticmethod
    def norm(config):
        return {
            "library": {
                "name": config["library"]["name"],
                "language": config["library"]["language"],
                "bmi_include": config["library"]["bmi_include"],
                "entry_point": config["library"]["entry_point"],
            },
            "build": {
                "undef_macros": config["build"].get("undef_macros", []),
                "define_macros": config["build"].get("define_macros", []),
                "libraries": config["build"].get("libraries", []),
                "library_dirs": config["build"].get("library_dirs", []),
                "include_dirs": config["build"].get("include_dirs", []),
                "extra_compile_args": config["build"].get("extra_compile_args", []),
            },
            "plugin": {
                "name": config["plugin"]["name"],
                "module": config["plugin"]["module"],
                "class": config["plugin"]["class"],
                "conda_package": config["plugin"]["conda_package"],
            },
            "info": {
                "plugin_author": config["info"]["plugin_author"],
                "github_username": config["info"]["github_username"],
                "plugin_license": config["info"]["plugin_license"],
                "summary": config["info"]["summary"],
            },
        }

    def dump(self, fp):
        yaml.safe_dump(self._meta, fp, default_flow_style=False)

    def as_cookiecutter_context(self):
        return {
            "full_name": self._meta["info"]["plugin_author"],
            "github_username": self._meta["info"]["github_username"],
            "plugin_name": self._meta["plugin"]["name"],
            "plugin_name": self._meta["plugin"]["module"],
            "plugin_class": self._meta["plugin"]["class"],
            "plugin_conda_package": self._meta["plugin"]["conda_package"],
            "bmi_include": self._meta["library"]["bmi_include"],
            "bmi_register": self._meta["library"]["entry_point"],
            # "class_name": self._meta["pymt"]["class_name"],
            "language": self._meta["library"]["language"],
            "undef_macros": ",".join(self._meta["build"]["undef_macros"]),
            "define_macros": ",".join(self._meta["build"]["define_macros"]),
            "libraries": ",".join(self._meta["build"]["libraries"]),
            "library_dirs": ",".join(self._meta["build"]["library_dirs"]),
            "include_dirs": ",".join(self._meta["build"]["include_dirs"]),
            "extra_compile_args": ",".join(self._meta["build"]["extra_compile_args"]),
            "open_source_license": self._meta["info"]["plugin_license"],
            "project_short_description": self._meta["info"]["summary"],
        }


@click.command()
@click.version_option(version=__version__)
@click.option("--compile", is_flag=True, help="compile the extension module")
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
    "--template",
    default="http://github.com/mcflugen/cookiecutter-bmi-wrap",
    help="Location of cookiecutter template",
)
@click.argument("meta", type=click.File(mode="r"))
@click.argument(
    "output",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
)
def main(meta, output, compile, clobber, template, quiet, verbose):

    config = PluginMetadata(meta)

    if not quiet:
        click.secho("reading template from {}".format(template), err=True)

    path = render_plugin_repo(
        config.as_cookiecutter_context(),
        output_dir=output,
        template=template,
        clobber=clobber,
    )

    with open(os.path.join(path, "plugin.yaml"), "w") as fp:
        config.dump(fp)

    if not quiet:
        click.secho("Your pymt plugin can be found at {}".format(path), fg="green")

    if compile:
        with cd(path):
            system(["versioneer", "install"])
            system(["python", "setup.py", "develop"])
    elif not quiet:
        click.secho("Skipping compile step. You can do this later with:", fg="white")
        click.secho("    $ cd {0}".format(path), fg="white")
        click.secho("    $ versioneer install", fg="white")
        click.secho("    $ python setup.py develop", fg="white")

    if not quiet:
        click.secho(
            "Don't forget to drop model metadata files into {0}".format(
                os.path.join(path, "meta")
            ),
            fg="green",
        )


def render_plugin_repo(context, output_dir=".", clobber=False, template=None):
    template = template or _TEMPLATE_URI

    cookiecutter(
        template,
        extra_context=context,
        output_dir=output_dir,
        no_input=True,
        overwrite_if_exists=clobber,
    )

    path = os.path.join(output_dir, "pymt_{}".format(context["plugin_name"]))
    if not os.path.isdir(path):
        raise RenderError("error creating {}".format(path))

    return path


if __name__ == "__main__":
    main(auto_envvar_prefix="BMI_WRAP")
