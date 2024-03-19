import os


def render(plugin_metadata) -> str:
    """Render _bmi.py."""
    languages = {
        library["language"] for library in plugin_metadata._meta["library"].values()
    }
    assert len(languages) == 1
    language = languages.pop()

    if language == "python":
        return _render_bmi_py(plugin_metadata)
    else:
        return _render_bmi_c(plugin_metadata)


def _render_bmi_c(plugin_metadata) -> str:
    """Render _bmi.py for a non-python library."""
    languages = [
        library["language"] for library in plugin_metadata._meta["library"].values()
    ]
    language = languages[0]
    assert language in ("c", "c++", "fortran")

    imports = [
        f"from {plugin_metadata.get('package', 'name')}.lib import {cls}"
        for cls in plugin_metadata._meta["library"]
    ]

    names = [
        f"    {cls!r},".replace("'", '"') for cls in plugin_metadata._meta["library"]
    ]

    return f"""\
{os.linesep.join(sorted(imports))}

__all__ = [
{os.linesep.join(sorted(names))}
]\
"""


def _render_bmi_py(plugin_metadata) -> str:
    """Render _bmi.py for a python library."""
    languages = [
        library["language"] for library in plugin_metadata._meta["library"].values()
    ]
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
        for cls, component in plugin_metadata._meta["library"].items()
    ]

    rename = [
        f"""\
{cls}.__name__ = {cls!r}
{cls}.METADATA = str(importlib_resources.files(__name__) / "data/{cls}")
""".replace(
            "'", '"'
        )
        for cls in plugin_metadata._meta["library"]
    ]

    names = [
        f"    {cls!r},".replace("'", '"') for cls in plugin_metadata._meta["library"]
    ]

    return f"""\
{header}
{os.linesep.join(sorted(imports))}

{os.linesep.join(sorted(rename))}

__all__ = [
{os.linesep.join(sorted(names))}
]\
"""
