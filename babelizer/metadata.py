"""Library metadata used by the babelizer to wrap libraries."""

from __future__ import annotations

import io
import pathlib
import sys
import warnings
from collections import defaultdict
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterable
from collections.abc import Mapping
from contextlib import suppress
from typing import Any

import tomli_w
import yaml

if sys.version_info >= (3, 11):  # pragma: no cover (PY11+)
    import tomllib
else:  # pragma: no cover (<PY311)
    import tomli as tomllib

from babelizer.errors import ScanError
from babelizer.errors import ValidationError


def validate_dict(
    meta: dict[str, Any],
    required: Iterable[str] | None = None,
    optional: Iterable[str] | None = None,
) -> None:
    """Validate babelizer configuration metadata.

    Parameters
    ----------
    meta : dict
        Configuration metadata
    required : dict, optional
        Required keys in configuration.
    optional : dict, optional
        Optional keys in configuration.

    Raises
    ------
    ValidationError
        Raised for invalid metadata.
    """
    actual = set(meta)
    required = set() if required is None else set(required)
    optional = required if optional is None else set(optional)
    valid = required | optional

    if missing := required - actual:
        raise ValidationError(
            "missing required key{}: {}".format(
                "s" if len(missing) > 1 else "", ", ".join(missing)
            )
        )

    if unknown := actual - valid:
        raise ValidationError(
            "unknown key{}: {}".format(
                "s" if len(unknown) > 1 else "", ", ".join(unknown)
            )
        )


def _norm_os(name: str) -> str:
    if name == "linux":
        name = "ubuntu"
    elif name == "mac":
        name = "macos"
    if not name.endswith("-latest"):
        name += "-latest"
    return name


class BabelMetadata(Mapping[str, Any]):
    """Library metadata."""

    LOADERS: dict[str, Callable[[str], dict[str, Any]]] = {
        "yaml": yaml.safe_load,
        "toml": tomllib.loads,
    }

    def __init__(
        self,
        library: dict[str, Any] | None = None,
        build: dict[str, Any] | None = None,
        package: dict[str, Any] | None = None,
        info: dict[str, Any] | None = None,
        plugin: dict[str, Any] | None = None,
        ci: dict[str, Any] | None = None,
    ):
        """Metadata used by the babelizer to wrap a library.

        Parameters
        ----------
        library : dict, optional
            Information about the library being babelized.
        build : dict, optional
            User-specified compiler flags.
        package : dict, optional
            Name and requirements to build the babelized library.
        info : dict, optional
            Descriptive information about the package.
        plugin : dict, optional
            Deprecated, use package.
        ci : dict, optional
            Information about how to set up continuous integration.
        """
        if plugin is not None:
            warnings.warn(
                "use 'package' instead of 'plugin'", DeprecationWarning, stacklevel=2
            )
            if package is not None:
                raise ValueError("specify one of 'package' or 'plugin', not both")
            package = plugin

        config = {
            "library": dict(library or {}),
            "build": dict(build or {}),
            "package": dict(package or {}),
            "info": dict(info or {}),
            "ci": dict(ci or {}),
        }

        BabelMetadata.validate(config)

        self._meta = BabelMetadata.norm(config)

    def __getitem__(self, key: str) -> dict[str, Any]:
        return self._meta[key]

    def __iter__(self) -> Generator[str, None, None]:
        yield from self._meta

    def __len__(self) -> int:
        return len(self._meta)

    @classmethod
    def from_stream(cls, stream: io.TextIOBase, fmt: str = "toml") -> BabelMetadata:
        """Create an instance of BabelMetadata from a file-like object.

        Parameters
        ----------
        stream : file-like
            File object with a babelizer configuration
        fmt : str, optional
            File format.

        Returns
        -------
        BabelMetadata
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
        except tomllib.TOMLDecodeError as error:
            raise ScanError(f"unable to scan toml-formatted metadata file:\n{error}")
        else:
            if not isinstance(meta, dict):
                raise ValidationError("metadata file does not contain a mapping object")
        return cls(**meta)

    @classmethod
    def from_path(cls, filepath: str) -> BabelMetadata:
        """Create an instance of BabelMetadata from a path-like object.

        Parameters
        ----------
        filepath : str
            Path to a babelizer configuration file.

        Returns
        -------
            A BabelMetadata instance.
        """
        path = pathlib.Path(filepath)

        with open(filepath) as fp:
            return BabelMetadata.from_stream(fp, fmt=path.suffix[1:])

    @staticmethod
    def validate(config: dict[str, Any]) -> None:
        """Ensure babelizer configuration metadata are valid.

        Parameters
        ----------
        config : dict
            Metadata to babelize a library.

        Raises
        ------
        ValidationError
            If metadata are not valid.
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
            for _babelized_class, library in libraries.items():
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
            warnings.warn(
                "use 'package' instead of 'plugin'", DeprecationWarning, stacklevel=2
            )

    @staticmethod
    def _handle_old_style_entry_points(library: dict[str, Any]) -> dict[str, Any]:
        def _header_ext(language: str) -> str:
            try:
                return {"c": ".h", "c++": ".hxx"}[language]
            except KeyError:
                return ""

        language = library["language"]
        if isinstance(entry_points := library["entry_point"], str):
            entry_points = [entry_points]

        libraries = {}
        for entry_point in entry_points:
            babelized_class, library_name, class_name = BabelMetadata.parse_entry_point(
                entry_point
            )
            libraries[babelized_class] = {
                "language": language,
                "library": library_name,
                "header": library_name + _header_ext(language),
                "entry_point": class_name,
            }

        return libraries

    @staticmethod
    def _handle_old_style_info(info: dict[str, Any]) -> dict[str, Any]:
        return {
            "package_author": info["plugin_author"],
            "package_author_email": info["plugin_author_email"],
            "github_username": info["github_username"],
            "package_license": info["plugin_license"],
            "summary": info["summary"],
        }

    @staticmethod
    def norm(config: dict[str, Any]) -> dict[str, Any]:
        """Ensure current style metadata are used in babelizer configuration.

        Parameters
        ----------
        config : dict
            Metadata to babelize a library.

        Return
        ------
        dict
            A dict of babelizer configuration metadata.
        """
        build: dict[str, list[str]] = defaultdict(list)
        with suppress(KeyError):
            build.update(config["build"])

        if "entry_point" in config["library"]:
            libraries = BabelMetadata._handle_old_style_entry_points(config["library"])
        else:
            libraries = {k: dict(v) for k, v in config["library"].items()}

        if "plugin_author" in config["info"]:
            info = BabelMetadata._handle_old_style_info(config["info"])
        else:
            info = config["info"]

        if "all" in config["ci"]["os"]:
            config["ci"] = ["linux", "mac", "windows"]

        languages = [lib["language"] for lib in config["library"].values()]
        language = languages[0]

        return {
            "library": libraries,
            "components": config["library"],
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
            "package_name": config["package"]["name"],
            "package_requirements": ",".join(config["package"]["requirements"]),
            "language": language,
            "open_source_license": config["info"]["package_license"],
        }

    def dump(self, fp: io.TextIOBase, fmt: str = "toml") -> None:
        """Write serialized metadata to a file.

        Parameters
        ----------
        fp : file-like
            File object for output.
        fmt : str, optional
            Format to serialize data.
        """
        print(self.format(fmt=fmt), file=fp, end="")

    def format(self, fmt: str = "toml") -> str:
        """Serialize metadata to output format.

        Parameters
        ----------
        fmt : str, optional
            Output format.

        Returns
        -------
        metadata : str
            Serialized metadata.
        """
        return getattr(self, f"format_{fmt}")()

    def format_toml(self) -> str:
        """Serialize metadata as TOML.

        Returns
        -------
        str
            Serialized metadata as a TOML-formatted string
        """
        return tomli_w.dumps(self._meta, multiline_strings=True)

    @staticmethod
    def parse_entry_point(specifier: str) -> tuple[str, str, str]:
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
        ...
        babelizer.errors.ValidationError: bad entry point specifier (bar:Baz). specifier must be of the form name=module:class
        """
        try:
            name, value = (item.strip() for item in specifier.split("="))
            module, obj = (item.strip() for item in value.split(":"))
        except ValueError:
            raise ValidationError(
                f"bad entry point specifier ({specifier}). specifier must be of"
                " the form name=module:class"
            ) from None

        return name, module, obj

    def as_cookiecutter_context(self) -> dict[str, Any]:
        """Format metadata in cookiecutter context.

        Returns
        -------
        dict
            Metadata in cookiecutter context.
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
