"""Utility functions used by the babelizer."""

from __future__ import annotations

import pathlib
import subprocess
import sys
from collections.abc import Generator
from collections.abc import Iterable
from collections.abc import Sequence
from contextlib import contextmanager
from contextlib import suppress

from babelizer.errors import SetupPyError


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
