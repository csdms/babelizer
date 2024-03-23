from __future__ import annotations

import os
from typing import Any

from jinja2 import Environment
from jinja2 import FileSystemLoader

from babelizer._datadir import get_datadir


def render(context: dict[str, Any]) -> str:
    languages = {
        library["language"]
        for library in context["cookiecutter"]["components"].values()
    }
    assert len(languages) == 1
    language = languages.pop()

    env = Environment(loader=FileSystemLoader(get_datadir()))

    path_to_template = os.path.join(
        "{{cookiecutter.package_name}}",
        "{{cookiecutter.package_name}}",
        "lib",
        f"_{language}.pyx",
    )
    template = env.get_template(path_to_template)

    return template.render(**context)
