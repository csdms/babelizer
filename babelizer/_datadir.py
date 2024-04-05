from __future__ import annotations

import sys

if sys.version_info >= (3, 12):  # pragma: no cover (PY12+)
    import importlib.resources as importlib_resources
else:  # pragma: no cover (<PY312)
    import importlib_resources


def get_datadir() -> str:
    return str(importlib_resources.files("babelizer") / "data")


def get_template_dir() -> str:
    return str(importlib_resources.files("babelizer") / "data" / "templates")
