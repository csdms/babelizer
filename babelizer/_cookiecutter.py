from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import StrictUndefined
from jinja2 import Template

from babelizer._post_hook import run
from babelizer._utils import as_cwd


def cookiecutter(
    template: str,
    extra_context: dict[str, Any] | None = None,
    output_dir: str = ".",
    no_input: bool = True,
    overwrite_if_exists: bool = False,
) -> None:
    if extra_context is None:
        extra_context = {}
    env = Environment(loader=FileSystemLoader(template), undefined=StrictUndefined)

    def datetime_format(value: datetime, format_: str = "%Y-%M-%D") -> str:
        return value.strftime(format_)

    env.filters["datetimeformat"] = datetime_format

    for dirpath, _dirnames, filenames in os.walk(template):
        rel_path = os.path.relpath(dirpath, template)
        target_dir = os.path.join(output_dir, render_path(rel_path, extra_context))

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        for filename in filenames:
            target_path = os.path.join(target_dir, render_path(filename, extra_context))

            with open(target_path, "w") as fp:
                fp.write(
                    env.get_template(os.path.join(rel_path, filename)).render(
                        **extra_context
                    )
                )

    with as_cwd(output_dir):
        run(extra_context)


def render_path(path: str, context: dict[str, Any]) -> str:
    rendered_path = Template(path).render(**context)

    root, ext = os.path.splitext(rendered_path)
    if ext == ".jinja":
        rendered_path = root

    return rendered_path
