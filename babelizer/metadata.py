import pathlib
import re
import warnings
from collections import OrderedDict, defaultdict

import tomlkit as toml
import yaml

from .errors import ScanError, ValidationError


def _setup_yaml_with_canonical_dict():
    """https://stackoverflow.com/a/8661021"""
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


def validate_dict(meta, required=None, optional=None):
    """Validate babelizer configuration metadata.

    Args:
        meta (dict): Configuration metadata
        required (dict, optional): Required keys in configuration. Defaults to None.
        optional (dict, optional): Optional keys in configuration. Defaults to None.

    Raises:
        ValidationError: Raised for invalid metadata
    """
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


def _norm_os(name):
    if name == "linux":
        name = "ubuntu"
    elif name == "mac":
        name = "macos"
    if not name.endswith("-latest"):
        name += "-latest"
    return name


class BabelMetadata:

    LOADERS = {"yaml": yaml.safe_load, "toml": toml.parse}

    def __init__(
        self, library=None, build=None, package=None, info=None, plugin=None, ci=None
    ):
        """Metadata used by the babelizer to wrap a library.

        Args:
            library (dict, optional): Information about the library being babelized. Defaults to None.
            build (dict, optional): User-specified compiler flags. Defaults to None.
            package (dict, optional): Name and requirements to build the babelized library. Defaults to None.
            info (dict, optional): Descriptive information about the package. Defaults to None.
            plugin (dict, optional): Deprecated, use package. Defaults to None.
            ci (dict, optional): Information about how to set up continuous integration. Defaults to None.
        """
        if plugin is not None:
            warnings.warn("use 'package' instead of 'plugin'", DeprecationWarning)
            if package is not None:
                raise ValueError("specify one of 'package' or 'plugin', not both")
            package = plugin

        config = {
            "library": library or {},
            "build": build or {},
            "package": package or {},
            "info": info or {},
            "ci": ci or {},
        }

        BabelMetadata.validate(config)

        self._meta = BabelMetadata.norm(config)

    @classmethod
    def from_stream(cls, stream, fmt="yaml"):
        """Create an instance of BabelMetadata from a file-like object.

        Args:
            stream (file object): File object with a babelizer configuration
            fmt (str, optional): File format. Defaults to "yaml".

        Returns:
            A BabelMetadata instance.
        """
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
        """Create an instance of BabelMetadata from a path-like object.

        Args:
            filepath (str): Path to a babelizer configuration file.

        Returns:
            A BabelMetadata instance.
        """
        path = pathlib.Path(filepath)

        with open(filepath, "r") as fp:
            return BabelMetadata.from_stream(fp, fmt=path.suffix[1:])

    def get(self, section, value):
        """Get a metadata value from the given section.

        Args:
            section (str): Section name.
            value (str): Key name.

        Returns:
            Metadata value.
        """
        return self._meta[section][value]

    @staticmethod
    def validate(config):
        """Ensure babelizer configuration metadata are valid.

        Args:
            config (dict): Metadata to babelize a library.

        Raises:
            ValidationError: if metadata are not valid.
        """
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
                validate_dict(
                    library,
                    required={"language", "library", "header", "entry_point"},
                    optional={},
                )

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
        validate_dict(config["ci"], required=("python_version", "os"), optional={})

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
            babelized_class, library, class_name = BabelMetadata.parse_entry_point(
                entry_point
            )
            libraries[babelized_class] = {
                "language": language,
                "library": library,
                "header": library + _header_ext(language),
                "entry_point": class_name,
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
        """Ensure current style metadata are used in babelizer configuration.

        Args:
            config (dict): Metadata to babelize a library.

        Returns:
            A dict of babelizer configuration metadata.
        """
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

        if "all" in config["ci"]["os"]:
            config["ci"] = ["linux", "mac", "windows"]

        return {
            "library": libraries,
            "build": {
                "undef_macros": build["undef_macros"],
                "define_macros": build["define_macros"],
                "libraries": build["libraries"],
                "library_dirs": build["library_dirs"],
                "include_dirs": build["include_dirs"],
                "extra_compile_args": build["extra_compile_args"],
            },
            "package": {
                "name": config["package"]["name"],
                "requirements": sorted(config["package"]["requirements"]),
            },
            "info": info,
            "ci": {
                "python_version": sorted(config["ci"]["python_version"]),
                "os": sorted(config["ci"]["os"]),
            },
        }

    def dump(self, fp, fmt="yaml"):
        """Write serialized metadata to a file.

        Args:
            fp (file object): File object for output.
            fmt (str, optional): [description]. Defaults to "yaml".
        """
        print(self.format(fmt=fmt), file=fp)

    def format(self, fmt="yaml"):
        """Serialize metadata to output format

        Args:
            fmt (str, optional): Output format. Defaults to "yaml".

        Returns:
            Serialized metadata.
        """
        return getattr(self, f"format_{fmt}")()

    def format_yaml(self):
        """Serialize metadata as YAML.

        Returns:
            str: Serialized metadata as a YAML-formatted string
        """
        import io

        contents = io.StringIO()
        yaml.safe_dump(self._meta, contents, default_flow_style=False)
        return contents.getvalue()

    def format_toml(self):
        """Serialize metadata as TOML.

        Returns:
            str: Serialized metadata as a TOML-formatted string
        """
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
        tuple of str
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
        """Format metadata in cookiecutter context.

        Returns:
            dict: Metadata in cookiecutter context.
        """
        languages = [lib["language"] for lib in self._meta["library"].values()]
        language = languages[0]
        platforms = [_norm_os(name) for name in self._meta["ci"]["os"]]

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
            "ci": {
                "os": platforms,
                "python_version": self._meta["ci"]["python_version"],
            },
            "package_name": self._meta["package"]["name"],
            "package_requirements": ",".join(self._meta["package"]["requirements"]),
            "language": language,
            "open_source_license": self._meta["info"]["package_license"],
        }
