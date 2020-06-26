#! /usr/bin/env python
import os
import pkg_resources
import re
from collections import OrderedDict

import click
import yaml
from cookiecutter.main import cookiecutter

from scripting.contexts import cd
from scripting.unix import system

from .. import __version__


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
        if isinstance(value, str):
            return False
        for item in value:
            if not isinstance(item, str):
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
        "library": ("language", "entry_point"),
        "plugin": ("name", "requirements"),
        "info": ("plugin_author", "github_username", "plugin_license", "summary"),
    }

    def __init__(self, filepath):
        self._meta = PluginMetadata.norm(yaml.load(filepath))
        validate_meta(self._meta)

    def get(self, section, value):
        return self._meta[section][value]

    @staticmethod
    def norm(config):
        if "build" not in config:
            config["build"] = {}
        return {
            "library": {
                "language": config["library"]["language"],
                "entry_point": config["library"]["entry_point"],
                "register": config["library"].get("register", ""),
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
                "requirements": config["plugin"]["requirements"],
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

    @staticmethod
    def parse_entry_point(specifier):
        name, value = specifier.split("=")
        module, obj = value.split(":")

        return name.strip(), module.strip(), obj.strip()

    def as_cookiecutter_context(self):
        language = self._meta["library"]["language"]
        plugin_module = ""
        plugin_class = ""
        entry_point = ""

        entry_points = self._meta["library"]["entry_point"]
        if isinstance(entry_points, str):
            entry_points = [entry_points]
        entry_points = ",".join(entry_points)

        return {
            "entry_points": entry_points,
            "full_name": self._meta["info"]["plugin_author"],
            "github_username": self._meta["info"]["github_username"],
            "plugin_name": self._meta["plugin"]["name"],
            "plugin_module": plugin_module,
            "plugin_class": plugin_class,
            "pymt_class": entry_point,
            "plugin_requirements": ",".join(self._meta["plugin"]["requirements"]),
            "bmi_register": "",
            "language": language,
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
    default=None,
    # default="http://github.com/mcflugen/cookiecutter-bmi-wrap",
    help="Location of cookiecutter template",
)
@click.argument("meta", type=click.File(mode="r"))
@click.argument(
    "output",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
)
def main(meta, output, compile, clobber, template, quiet, verbose):

    config = PluginMetadata(meta)

    template = template or pkg_resources.resource_filename("bmi_wrap", "data")

    if not quiet:
        click.secho("reading template from {}".format(template), err=True)

    path = render_plugin_repo(
        template,
        context=config.as_cookiecutter_context(),
        output_dir=output,
        clobber=clobber,
    )

    with open(os.path.join(path, "plugin.yaml"), "w") as fp:
        config.dump(fp)

    if not quiet:
        click.secho("Your pymt plugin can be found at {}".format(path), fg="green")

    click.secho("Checklist of things to do:", fg="white")
    checklist = OrderedDict(
        [
            ("versioneer install", " "),
            ("make install", " "),
            ("make pretty", " "),
            ("make lint", " "),
            ("make docs", " "),
        ]
    )
    if compile:
        with cd(path):
            system(["versioneer", "install"])
            system(["python", "setup.py", "develop"])
        checklist["version"] = "x"
        checklist["install"] = "x"
    if not quiet:
        for item, status in checklist.items():
            click.secho(
                "[{status}] {item}".format(item=item, status=status), fg="white"
            )

    if not quiet:
        click.secho(
            "Don't forget to drop model metadata files into {0}".format(
                os.path.join(path, "meta")
            ),
            fg="green",
        )


def render_plugin_repo(template, context=None, output_dir=".", clobber=False):
    """Render a repository for a pymt plugin.

    Parameters
    ----------
    template: bool
        Path (or URL) to the cookiecutter template to use.
    context: dict, optional
        Context for the new repository.
    output_dir : str, optional
        Name of the folder that will be the new repository.
    clobber: bool, optional
        If a like-named repository already exists, overwrite it.

    Returns
    -------
    path
        Absolute path to the newly-created repository.
    """
    context = context or {}

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
