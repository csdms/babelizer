import os


def render(plugin_metadata) -> str:
    """Render lib/__init__.py."""
    package_name = plugin_metadata.get("package", "name")
    imports = [
        f"from {package_name}.lib.{cls.lower()} import {cls}"
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
