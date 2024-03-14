import os


def render(plugin_metadata) -> str:
    """Render __init__.py."""
    package_name = plugin_metadata.get("package", "name")

    imports = [f"from {package_name}._version import __version__"]
    imports += [
        f"from {package_name}._bmi import {cls}"
        for cls in plugin_metadata._meta["library"]
    ]

    names = [
        f"    {cls!r},".replace("'", '"') for cls in plugin_metadata._meta["library"]
    ]

    return f"""\
{os.linesep.join(sorted(imports))}

__all__ = [
    "__version__",
{os.linesep.join(sorted(names))}
]\
"""
