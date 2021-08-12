import pathlib
import subprocess
import sys
from contextlib import contextmanager

from .errors import SetupPyError


def execute(args):
    """Run a command through the ``subprocess`` module.

    Args:
        args (list): Command and arguments to command.

    Returns:
        results from ``subprocess.run``.
    """
    return subprocess.run(args, capture_output=True, check=True)


def setup_py(*args):
    """Format the command to build/install the babelized package.

    Returns:
        list of str: The build/install command.
    """
    return [sys.executable, "setup.py"] + list(args)


def get_setup_py_version():
    """Get babelized package version.

    Raises:
        SetupPyError: if calling ``python setup.py`` raises an exception.

    Returns:
        str or None: Package version.
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
def save_files(files):
    """[summary]

    Args:
        files ([type]): [description]

    Yields:
        [type]: [description]
    """
    contents = {}
    for file_ in files:
        try:
            with open(file_, "r") as fp:
                contents[file_] = fp.read()
        except FileNotFoundError:
            pass
    yield contents
    for file_ in contents:
        with open(file_, "w") as fp:
            fp.write(contents[file_])
