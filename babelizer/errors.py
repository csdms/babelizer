"""Exceptions raised by the *babelizer*."""


class BabelizeError(Exception):
    """An exception that the babelizer can handle and show to the user."""

    def __init__(self, message):
        self._message = message

    def __str__(self):
        """Render a user-readable error message."""
        return self._message


class ValidationError(BabelizeError):
    """Raised if babelizer configuration data are incorrectly formatted."""

    pass


class RenderError(BabelizeError):
    """Raised if the babelizer encounters an error in creating output files."""

    pass


class ScanError(BabelizeError):
    """Raised if babelizer configuration file is incorrectly formatted."""

    pass


class OutputDirExistsError(BabelizeError):
    """An exception used when the directory for babelized output exists."""

    pass


class SetupPyError(BabelizeError):
    """Raised if the babelized package cannot be built through setup.py."""

    pass
