from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any


def render(plugin_metadata: Mapping[str, Any]) -> str:
    """Render lib/__init__.py."""
    package_name = plugin_metadata["package"]["name"]
    imports = [
        f"from {package_name}.lib.{cls.lower()} import {cls}"
        for cls in plugin_metadata["library"]
    ]

    names = [f"    {cls!r},".replace("'", '"') for cls in plugin_metadata["library"]]

    return f"""\
{os.linesep.join(sorted(imports))}

__all__ = [
{os.linesep.join(sorted(names))}
]\
"""
