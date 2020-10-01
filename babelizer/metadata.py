import pathlib
import re
import warnings
from collections import OrderedDict, defaultdict

import tomlkit as toml
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


def validate_dict(meta, required=None, optional=None):
    actual = set(meta)
    required = set() if required is None else set(required)
    optional = required if optional is None else set(optional)
    valid = required | optional

    if missing := required - actual:
        raise ValidationError(
            "missing required key{0}: {1}".format(
                "s" if len(missing) > 1 else "", ", ".join(missing)
            )
        )

    if unknown := actual - valid:
        raise ValidationError(
            "unknown key{0}: {1}".format(
                "s" if len(unknown) > 1 else "", ", ".join(unknown)
            )
        )


class BabelMetadata:
    REQUIRED = {
        "library": ("language", "entry_point"),
        "package": ("name", "requirements"),
        "info": ("github_username", "package_license", "summary"),
    }

    LOADERS = {"yaml": yaml.safe_load, "toml": toml.parse}

    def __init__(self, library=None, build=None, package=None, info=None, plugin=None):
        if plugin is not None:
            warnings.warn("use 'package' instead of 'plugin'", DeprecationWarning)
            if package is not None:
                raise ValueError("specify one of 'package' or 'plugin', not both")
            package = plugin

        config = {
            "library": library or {},
            "build": build or {},
            "package": package or {},
            "info": info or {}
        }

        BabelMetadata.validate(config)

        self._meta = BabelMetadata.norm(config)

    @classmethod
    def from_stream(cls, stream, fmt="yaml"):
        try:
            loader = BabelMetadata.LOADERS[fmt]
        except KeyError:
            raise ValueError(f"unrecognized format ({fmt})")

        try:
            meta = loader(stream.read())
        except yaml.scanner.ScannerError as error:
            raise ScanError(f"unable to scan yaml-formatted metadata file:\n{error}")
        except toml.exceptions.ParseError as error:
            raise ScanError(f"unable to scan toml-formatted metadata file:\n{error}")
        else:
            if not isinstance(meta, dict):
                raise ValidationError("metadata file does not contain a mapping object")
        return cls(**meta)

    @classmethod
    def from_path(cls, filepath):
        path = pathlib.Path(filepath)

        with open(filepath, "r") as fp:
            return BabelMetadata.from_stream(fp, fmt=path.suffix[1:])

    def get(self, section, value):
        return self._meta[section][value]

    @staticmethod
    def validate(config):
        libraries = config["library"]
        if "entry_point" in libraries:
            validate_dict(libraries, required=("language", "entry_point"), optional={})
            for entry_point in libraries["entry_point"]:
                try:
                    BabelMetadata.parse_entry_point(entry_point)
                except ValidationError:
                    raise ValidationError(f"poorly-formed entry point ({entry_point})")
        else:
            for babelized_class, library in libraries.items():
                validate_dict(library, required={"language", "library", "header", "class"}, optional={})

        validate_dict(
            config["build"],
            required=None,
            optional=(
                "undef_macros",
                "define_macros",
                "libraries",
                "library_dirs",
                "include_dirs",
                "extra_compile_args",
            ),
        )
        validate_dict(config["package"], required=("name", "requirements"), optional={})
        try:
            validate_dict(
                config["info"],
                required=(
                    "package_author",
                    "package_author_email",
                    "github_username",
                    "package_license",
                    "summary",
                ),
                optional={},
            )
        except ValidationError:
            validate_dict(
                config["info"],
                required=(
                    "plugin_author",
                    "plugin_author_email",
                    "github_username",
                    "plugin_license",
                    "summary",
                ),
                optional={},
            )
            warnings.warn("use 'package' instead of 'plugin'", DeprecationWarning)

    @staticmethod
    def _handle_old_style_entry_points(library):
        def _header_ext(language):
            try:
                return {"c": ".h", "c++": ".hxx"}[language]
            except KeyError:
                return ""

        language = library["language"]
        if isinstance(entry_points := library["entry_point"], str):
            entry_points = [entry_points]

        libraries = {}
        for entry_point in entry_points:
            babelized_class, library, class_name = BabelMetadata.parse_entry_point(entry_point)
            libraries[babelized_class] = {
                "language": language,
                "library": library,
                "header": library + _header_ext(language),
                "class": class_name,
            }

        return libraries

    @staticmethod
    def _handle_old_style_info(info):
        return {
            "package_author": info["plugin_author"],
            "package_author_email": info["plugin_author_email"],
            "github_username": info["github_username"],
            "package_license": info["plugin_license"],
            "summary": info["summary"],
        }

    @staticmethod
    def norm(config):
        build = defaultdict(list)
        try:
            build.update(config["build"])
        except KeyError:
            pass

        if "entry_point" in config["library"]:
            libraries = BabelMetadata._handle_old_style_entry_points(config["library"])
        else:
            libraries = config["library"]

        if "plugin_author" in config["info"]:
            info = BabelMetadata._handle_old_style_info(config["info"])
        else:
            info = config["info"]

        return {
            "library": libraries,
            "build": {
                "undef_macros": build["undef_macros"],
                "undef_macros": build["undef_macros"],
                "define_macros": build["define_macros"],
                "libraries": build["libraries"],
                "library_dirs": build["library_dirs"],
                "include_dirs": build["include_dirs"],
                "extra_compile_args": build["extra_compile_args"],
            },
            "package": {
                "name": config["package"]["name"],
                "requirements": list(config["package"]["requirements"]),
            },
            "info": info,
        }

    def dump(self, fp, fmt="yaml"):
        print(self.format(fmt=fmt), file=fp)

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
        """Parse an entry point specifier into its parts.

        Parameters
        ----------
        specifier : str
            An entry-point specifier.

        Returns
        -------
        tupe of str
            The parts of the entry point as (*name*, *module*, *class*).

        Raises
        ------
        ValidationError
            If the entry point cannot be parsed.

        Examples
        --------
        >>> from babelizer.metadata import BabelMetadata
        >>> BabelMetadata.parse_entry_point("Foo=bar:Baz")
        ('Foo', 'bar', 'Baz')

        >>> BabelMetadata.parse_entry_point("bar:Baz")
        Traceback (most recent call last):
        ,,,
        babelizer.errors.ValidationError: bad entry point specifier (bar:Baz). specifier must be of the form name=module:class
        """
        try:
            name, value = [item.strip() for item in specifier.split("=")]
            module, obj = [item.strip() for item in value.split(":")]
        except ValueError:
            raise ValidationError(
                f"bad entry point specifier ({specifier}). specifier must be of the form name=module:class"
            ) from None

        return name, module, obj

    def as_cookiecutter_context(self):
        languages = [lib["language"] for lib in self._meta["library"].values()]
        language = languages[0]

        return {
            "components": self._meta["library"],
            "build": {
                "undef_macros": self._meta["build"]["undef_macros"],
                "define_macros": self._meta["build"]["define_macros"],
                "libraries": self._meta["build"]["libraries"],
                "library_dirs": self._meta["build"]["library_dirs"],
                "include_dirs": self._meta["build"]["include_dirs"],
                "extra_compile_args": self._meta["build"]["extra_compile_args"],
            },
            "info": {
                "full_name": self._meta["info"]["package_author"],
                "email": self._meta["info"]["package_author_email"],
                "github_username": self._meta["info"]["github_username"],
                "project_short_description": self._meta["info"]["summary"],
            },
            "package_name": self._meta["package"]["name"],
            "package_requirements": ",".join(self._meta["package"]["requirements"]),
            "language": language,
            "open_source_license": self._meta["info"]["package_license"],
        }
