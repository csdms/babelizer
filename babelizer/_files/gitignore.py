import os


def render(plugin_metadata) -> str:
    """Render a .gitignore file."""
    package_name = plugin_metadata.get("package", "name")

    languages = {
        library["language"] for library in plugin_metadata._meta["library"].values()
    }
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
            f"{package_name}/lib/{cls.lower()}.c"
            for cls in plugin_metadata._meta["library"]
        }

    if "fortran" in languages:
        ignore |= {"*.mod", "*.smod"}

    return f"{os.linesep.join(sorted(ignore))}"
