import pathlib
import re
from collections import OrderedDict

import toml
import yaml

from .errors import ScanError, ValidationError


def _setup_yaml_with_canonical_dict():
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
        "tag:yaml.org,2002:float",
        re.compile(
            """^(?:
         [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
        |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
        |\\.[0-9_]+(?:[eE][-+][0-9]+)?
        |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
        |[-+]?\\.(?:inf|Inf|INF)
        |\\.(?:nan|NaN|NAN))$""",
            re.X,
        ),
        list("-+0123456789."),
    )


_setup_yaml_with_canonical_dict()


def validate_meta(meta):
    missing_sections = set(BabelMetadata.REQUIRED) - set(meta)
    if missing_sections:
        raise ValidationError(
            "missing required sections {0}".format(", ".join(missing_sections))
        )

    for section, values in BabelMetadata.REQUIRED.items():
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


class BabelMetadata:
    REQUIRED = {
        "library": ("language", "entry_point"),
        "plugin": ("name", "requirements"),
        "info": ("github_username", "plugin_license", "summary"),
    }

    LOADERS = {"yaml": yaml.safe_load, "toml": toml.load}

    def __init__(self, library=None, build=None, plugin=None, info=None):
        self._meta = BabelMetadata.norm(
            {
                "library": library or {},
                "build": build or {},
                "plugin": plugin or {},
                "info": info or {},
            }
        )
        validate_meta(self._meta)

    @classmethod
    def from_stream(cls, stream, fmt="yaml"):
        try:
            loader = BabelMetadata.LOADERS[fmt]
        except KeyError:
            raise ValueError(f"unrecognized format ({fmt})")

        try:
            return cls(**loader(stream))
        except TypeError:
            raise ValidationError("metadata file does not contain a mapping object")
        except yaml.scanner.ScannerError as error:
            raise ScanError(
                f"unable to scan yaml-formatted metadata file:\n{error}"
            )
        except toml.TomlDecodeError as error:
            raise ScanError(
                f"unable to scan toml-formatted metadata file:\n{error}"
            )

    @classmethod
    def from_path(cls, filepath):
        path = pathlib.Path(filepath)

        with open(filepath, "r") as fp:
            return BabelMetadata.from_stream(fp, fmt=path.suffix[1:])

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

    def dump(self, fp, fmt="yaml"):
        print(self.format(fmt=fmt), file=fp)
        # yaml.safe_dump(self._meta, fp, default_flow_style=False)

    def format(self, fmt="yaml"):
        return getattr(self, f"format_{fmt}")()

    def format_yaml(self):
        import io

        contents = io.StringIO()
        yaml.safe_dump(self._meta, contents, default_flow_style=False)
        return contents.getvalue()

    def format_toml(self):
        return toml.dumps(self._meta)

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
