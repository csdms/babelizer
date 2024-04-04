from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any


def render(context: Mapping[str, Any]) -> str:
    """Render __init__.py."""
    package_name = context["package"]["name"]

    imports = [f"from {package_name}._version import __version__"]
    imports += [f"from {package_name}._bmi import {cls}" for cls in context["library"]]

    names = [f"    {cls!r},".replace("'", '"') for cls in context["library"]]

    return f"""\
{os.linesep.join(sorted(imports))}

__all__ = [
    "__version__",
{os.linesep.join(sorted(names))}
]\
"""
