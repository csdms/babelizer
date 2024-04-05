"""Library configuration used by the babelizer to wrap libraries."""

from __future__ import annotations

import io
import pathlib
import sys
import warnings
from collections import defaultdict
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Mapping
from contextlib import suppress
from typing import Any

import tomli_w
import yaml

if sys.version_info >= (3, 11):  # pragma: no cover (PY11+)
    import tomllib
else:  # pragma: no cover (<PY311)
    import tomli as tomllib

from babelizer._utils import parse_entry_point
from babelizer._utils import validate_dict_keys
from babelizer.errors import ScanError
from babelizer.errors import ValidationError


class BabelConfig(Mapping[str, Any]):
    """Babelizer configuration."""

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
        """Configuration used by the babelizer to wrap a library.

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

        BabelConfig.validate(config)

        self._meta = BabelConfig.norm(config)

    def __getitem__(self, key: str) -> dict[str, Any]:
        return self._meta[key]

    def __iter__(self) -> Generator[str, None, None]:
        yield from self._meta

    def __len__(self) -> int:
        return len(self._meta)

    @classmethod
    def from_stream(cls, stream: io.TextIOBase, fmt: str = "toml") -> BabelConfig:
        """Create an instance of BabelConfig from a file-like object.

        Parameters
        ----------
        stream : file-like
            File object with a babelizer configuration
        fmt : str, optional
            File format.

        Returns
        -------
        BabelConfig
            A BabelConfig instance.
        """
        try:
            loader = BabelConfig.LOADERS[fmt]
        except KeyError:
            raise ValueError(f"unrecognized format ({fmt})")

        try:
            meta = loader(stream.read())
        except yaml.scanner.ScannerError as error:
            raise ScanError(f"unable to scan yaml-formatted config file:\n{error}")
        except tomllib.TOMLDecodeError as error:
            raise ScanError(f"unable to scan toml-formatted config file:\n{error}")
        else:
            if not isinstance(meta, dict):
                raise ValidationError("config file does not contain a mapping object")
        return cls(**meta)

    @classmethod
    def from_path(cls, filepath: str) -> BabelConfig:
        """Create an instance of BabelConfig from a path-like object.

        Parameters
        ----------
        filepath : str
            Path to a babelizer configuration file.

        Returns
        -------
            A BabelConfig instance.
        """
        path = pathlib.Path(filepath)

        with open(filepath) as fp:
            return BabelConfig.from_stream(fp, fmt=path.suffix[1:])

    @staticmethod
    def validate(config: dict[str, Any]) -> None:
        """Ensure babelizer configuration is valid.

        Parameters
        ----------
        config : dict
            Configuration to babelize a library.

        Raises
        ------
        ValidationError
            If configuration is not valid.
        """
        libraries = config["library"]
        if "entry_point" in libraries:
            validate_dict_keys(
                libraries, required=("language", "entry_point"), optional={}
            )
            for entry_point in libraries["entry_point"]:
                try:
                    parse_entry_point(entry_point)
                except ValidationError:
                    raise ValidationError(f"poorly-formed entry point ({entry_point})")
        else:
            for _babelized_class, library in libraries.items():
                validate_dict_keys(
                    library,
                    required={"language", "library", "header", "entry_point"},
                    optional={},
                )

        validate_dict_keys(
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
        validate_dict_keys(
            config["package"], required=("name", "requirements"), optional={}
        )
        validate_dict_keys(config["ci"], required=("python_version", "os"), optional={})

        try:
            validate_dict_keys(
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
            validate_dict_keys(
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
            babelized_class, library_name, class_name = parse_entry_point(entry_point)
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
        """Ensure current style is used in babelizer configuration.

        Parameters
        ----------
        config : dict
            Configuration to babelize a library.

        Return
        ------
        dict
            A dict of babelizer configuration.
        """
        build: dict[str, list[str]] = defaultdict(list)
        with suppress(KeyError):
            build.update(config["build"])

        if "entry_point" in config["library"]:
            libraries = BabelConfig._handle_old_style_entry_points(config["library"])
        else:
            libraries = {k: dict(v) for k, v in config["library"].items()}

        if "plugin_author" in config["info"]:
            info = BabelConfig._handle_old_style_info(config["info"])
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
            "language": language,
        }

    def dump(self, fp: io.TextIOBase, fmt: str = "toml") -> None:
        """Write serialized configuration to a file.

        Parameters
        ----------
        fp : file-like
            File object for output.
        fmt : str, optional
            Format to serialize data.
        """
        print(self.format(fmt=fmt), file=fp, end="")

    def format(self, fmt: str = "toml") -> str:
        """Serialize configuration to output format.

        Parameters
        ----------
        fmt : str, optional
            Output format.

        Returns
        -------
        config : str
            Serialized configuration.
        """
        return getattr(self, f"format_{fmt}")()

    def format_toml(self) -> str:
        """Serialize configuration as TOML.

        Returns
        -------
        str
            Serialized configuration as a TOML-formatted string
        """
        return tomli_w.dumps(self._meta, multiline_strings=True)
