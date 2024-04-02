from __future__ import annotations

import os
from collections.abc import Iterable
from datetime import datetime
from typing import Any

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import StrictUndefined
from jinja2 import Template

from babelizer._datadir import get_template_dir
from babelizer._post_hook import run
from babelizer._utils import as_cwd


def cookiecutter(
    template: str,
    context: dict[str, Any] | None = None,
    output_dir: str = ".",
) -> None:
    if context is None:
        context = {}
    env = babelizer_environment(template)

    def datetime_format(value: datetime, format_: str = "%Y-%M-%D") -> str:
        return value.strftime(format_)

    env.filters["datetimeformat"] = datetime_format

    for dirpath, _dirnames, filenames in os.walk(template):
        rel_path = os.path.relpath(dirpath, template)
        target_dir = os.path.join(output_dir, render_path(rel_path, context))

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        for filename in filenames:
            target_path = os.path.join(target_dir, render_path(filename, context))

            with open(target_path, "w") as fp:
                fp.write(
                    env.get_template(os.path.join(rel_path, filename)).render(**context)
                )

    with as_cwd(output_dir):
        run(context)


def babelizer_environment(template: str | None = None) -> Environment:
    if template is None:
        template = get_template_dir()

    return Environment(loader=FileSystemLoader(template), undefined=StrictUndefined)


def render_path(
    path: str,
    context: dict[str, Any],
    remove_extension: Iterable[str] = (".jinja", ".jinja2", ".j2"),
) -> str:
    """Render a path as though it were a jinja template.

    Parameters
    ----------
    path : str
        A path.
    context : dict
        Context to use for substitution.
    remove_extension : iterable of str, optional
        If the provided path ends with one of these exensions,
        the extension will be removed from the rendered path.

    Examples
    --------
    >>> from babelizer._cookiecutter import render_path
    >>> render_path("{{foo}}.py", {"foo": "bar"})
    'bar.py'
    >>> render_path("{{foo}}.py.jinja", {"foo": "bar"})
    'bar.py'
    >>> render_path("bar.py.j2", {"foo": "bar"})
    'bar.py'
    >>> render_path("{{bar}}.py.jinja", {"foo": "bar"})
    Traceback (most recent call last):
    ...
    jinja2.exceptions.UndefinedError: 'bar' is undefined
    """
    rendered_path = Template(path, undefined=StrictUndefined).render(**context)

    root, ext = os.path.splitext(rendered_path)
    return rendered_path if ext not in remove_extension else root
