from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any


def render(context: Mapping[str, Any]) -> str:
    """Render a .gitignore file."""
    package_name = context["package"]["name"]

    languages = {library["language"] for library in context["library"].values()}
    ignore = {
        "*.egg-info/",
        "*.py[cod]",
        ".coverage",
        ".nox/",
        "__pycache__/",
        "build/",
        "dist/",
    }

    if "python" not in languages:
        ignore |= {"*.o", "*.so"} | {
            f"{package_name}/lib/{cls.lower()}.c" for cls in context["library"]
        }

    if "fortran" in languages:
        ignore |= {"*.mod", "*.smod"}

    return f"{os.linesep.join(sorted(ignore))}"
