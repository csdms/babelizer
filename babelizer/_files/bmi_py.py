from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any


def render(context: Mapping[str, Any]) -> str:
    """Render _bmi.py."""
    languages = {library["language"] for library in context["library"].values()}
    assert len(languages) == 1
    language = languages.pop()

    if language == "python":
        return _render_bmi_py(context)
    else:
        return _render_bmi_c(context)


def _render_bmi_c(context: Mapping[str, Any]) -> str:
    """Render _bmi.py for a non-python library."""
    languages = [library["language"] for library in context["library"].values()]
    language = languages[0]
    assert language in ("c", "c++", "fortran")

    imports = [
        f"from {context['package']['name']}.lib import {cls}"
        for cls in context["library"]
    ]

    names = [f"    {cls!r},".replace("'", '"') for cls in context["library"]]

    return f"""\
{os.linesep.join(sorted(imports))}

__all__ = [
{os.linesep.join(sorted(names))}
]\
"""


def _render_bmi_py(context: Mapping[str, Any]) -> str:
    """Render _bmi.py for a python library."""
    languages = [library["language"] for library in context["library"].values()]
    language = languages[0]
    assert language == "python"

    header = """\
import sys

if sys.version_info >= (3, 12):  # pragma: no cover (PY12+)
    import importlib.resources as importlib_resources
else:  # pragma: no cover (<PY312)
    import importlib_resources
"""

    imports = [
        f"from {component['library']} import {component['entry_point']} as {cls}"
        for cls, component in context["library"].items()
    ]

    rename = [
        f"""\
{cls}.__name__ = {cls!r}
{cls}.METADATA = str(importlib_resources.files(__name__) / "data/{cls}")
""".replace(
            "'", '"'
        )
        for cls in context["library"]
    ]

    names = [f"    {cls!r},".replace("'", '"') for cls in context["library"]]

    return f"""\
{header}
{os.linesep.join(sorted(imports))}

{os.linesep.join(sorted(rename))}

__all__ = [
{os.linesep.join(sorted(names))}
]\
"""
