from __future__ import annotations

from typing import Any

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import StrictUndefined

from babelizer._datadir import get_template_dir


def render(context: dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(get_template_dir()), undefined=StrictUndefined
    )
    template = env.get_template("templates/README.rst")

    return template.render(**context)
