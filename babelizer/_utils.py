"""Utility functions used by the babelizer."""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
from collections.abc import Generator
from collections.abc import Iterable
from collections.abc import Sequence
from contextlib import contextmanager
from contextlib import suppress
from typing import Any

from babelizer.errors import SetupPyError
from babelizer.errors import ValidationError


def execute(args: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
    """Run a command through the ``subprocess`` module.

    Parameters
    ----------
    args : list
        Command and arguments to command.

    Returns
    -------
    ~subprocess.CompletedProcess
        results from :func:`subprocess.run`.
    """
    return subprocess.run(args, capture_output=True, check=True)


def setup_py(*args: str) -> list[str]:
    """Format the command to build/install the babelized package.

    Returns
    -------
    list of str
        The build/install command.
    """
    return [sys.executable, "setup.py"] + list(args)


def get_setup_py_version() -> str | None:
    """Get babelized package version.

    Returns
    -------
    str or None
        Package version.

    Raises
    ------
    SetupPyError
        If calling ``python setup.py`` raises an exception.
    """
    if pathlib.Path("setup.py").exists():
        try:
            execute(setup_py("egg_info"))
        except subprocess.CalledProcessError as err:
            stderr = err.stderr.decode("utf-8")
            if "Traceback" in stderr:
                raise SetupPyError(stderr) from None
            return None
        result = execute(setup_py("--version"))
        return result.stdout.splitlines()[0].decode("utf-8")
    else:
        return None


@contextmanager
def save_files(files: Iterable[str]) -> Generator[dict[str, str], None, None]:
    """Generate repository files through a context.

    Parameters
    ----------
    files : list of str
        List of path-like objects.

    Yields
    ------
    str
        Generator for repository files.
    """
    contents = {}
    for file_ in files:
        with suppress(FileNotFoundError), open(file_) as fp:
            contents[file_] = fp.read()
    yield contents
    for file_ in contents:
        with open(file_, "w") as fp:
            fp.write(contents[file_])


@contextmanager
def as_cwd(path: str) -> Generator[None, None, None]:
    """Change directory context.

    Parameters
    ----------
    path : str
        Path-like object to a directory.
    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)


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
    >>> from babelizer._utils import parse_entry_point
    >>> parse_entry_point("Foo=bar:Baz")
    ('Foo', 'bar', 'Baz')

    >>> parse_entry_point("bar:Baz")
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


def validate_dict_keys(
    meta: dict[str, Any],
    required: Iterable[str] | None = None,
    optional: Iterable[str] | None = None,
) -> None:
    """Validate the keys of a dict.

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
