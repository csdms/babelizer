import os


def render(plugin_metadata) -> str:
    package_name = plugin_metadata.get("package", "name")

    languages = {
        library["language"] for library in plugin_metadata._meta["library"].values()
    }
    ignore = [
        "*.egg-info/",
        "*.py[cod]",
        ".coverage",
        "__pycache__/",
        "build/",
        "dist/",
    ]

    if "fortran" in languages:
        ignore += [
            f"{package_name}/lib/bmi_interoperability.mod",
            f"{package_name}/lib/bmi_interoperability.smod",
            f"{package_name}/lib/bmi_interoperability.o",
        ]
        ignore += [
            f"{package_name}/lib/{cls.lower()}.c"
            for cls in plugin_metadata._meta["library"]
        ]

    return f"{os.linesep.join(sorted(ignore))}"
