import os
from collections import defaultdict
from collections.abc import Iterable


def render(paths: Iterable[str], install: Iterable[str] = ()) -> str:
    """Render an example meson.build file.

    Parameters
    ----------
    paths : iterable of str
        Paths to cython extensions.
    install : iterable of str
        Paths to files to install.

    Returns
    -------
    str
        The contents of a meson.build file.
    """
    before = """\
project(
    'package_name',
    'c',
    'cython',
    version: '0.1.0',
)

py_mod = import('python')
py = py_mod.find_installation(pure: false)
py_dep = py.dependency()

numpy_inc = run_command(
    py,
    ['-c', 'import numpy; print(numpy.get_include())'],
    check: true,
).stdout().strip()\
"""

    files_to_install = _render_install_block(install)
    extensions = os.linesep.join(_render_extension_module(path) for path in paths)

    after = """\
# Install data files.
# install_subdir(
#     'data/',
#     install_dir: py.get_install_dir() / 'package_name/data',
# )

# This is a temporary fix for editable installs.
# run_command('cp', '-r', 'data/', 'build')\
"""
    contents = [before]
    if files_to_install:
        contents.append(files_to_install)
    if extensions:
        contents.append(extensions)
    contents.append(after)

    return (2 * os.linesep).join(contents)


def _render_install_block(install: Iterable[str]):
    install_sources = defaultdict(list)
    for root, fname in (os.path.split(src) for src in install):
        install_sources[root].append(fname)

    files_to_install = []
    for subdir, files in sorted(install_sources.items()):
        lines = [f"        {os.path.join(subdir, f)!r}," for f in files]
        files_to_install.append(
            f"""\
py.install_sources(
    [
{os.linesep.join(sorted(lines))}
    ],
    subdir: {subdir!r},
)\
"""
        )
    return os.linesep.join(files_to_install)


def _render_extension_module(path: str) -> str:
    root, ext = os.path.splitext(path)
    assert ext == ".pyx", f"{path} does not appear to be a cython file"

    module_name = root.replace(os.path.sep, ".")

    return f"""\
py.extension_module(
    {module_name!r},
    [{path!r}],
    include_directories: [
        {os.path.dirname(path)!r},
        numpy_inc,
    ],
    dependencies: [
        py.dependency(),
        # Dependencies required to build the extension.
        # dependency('another_package', method : 'pkg-config'),
    ],
    install: true,
    subdir: {os.path.dirname(path)!r},
)\
"""
