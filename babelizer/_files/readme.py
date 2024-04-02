from __future__ import annotations

from typing import Any

from babelizer._cookiecutter import babelizer_environment


def render(context: dict[str, Any]) -> str:
    template = babelizer_environment().get_template("README.rst")

    return template.render(**context)
