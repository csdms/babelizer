import pathlib

import black as blk
import yaml
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException
from isort import SortImports

from .errors import OutputDirExistsError, RenderError
from .metadata import PluginMetadata


def render(meta, output, template=None, clobber=False):
    config = PluginMetadata(meta)

    if template is None:
        template = pkg_resources.resource_filename("babelizer", "data")

    try:
        path = render_plugin_repo(
            template,
            context=config.as_cookiecutter_context(),
            output_dir=output,
            clobber=True,
        )
    except OutputDirExistsError as error:
        err(str(error))
        raise click.Abort()

    with open(path / "plugin.yaml", "w") as fp:
        config.dump(fp)

    prettify_python(path)

    return path.resolve()


def render_plugin_repo(template, context=None, output_dir=".", clobber=False):
    """Render a repository for a pymt plugin.

    Parameters
    ----------
    template: bool
        Path (or URL) to the cookiecutter template to use.
    context: dict, optional
        Context for the new repository.
    output_dir : str, optional
        Name of the folder that will be the new repository.
    clobber: bool, optional
        If a like-named repository already exists, overwrite it.

    Returns
    -------
    path
        Absolute path to the newly-created repository.
    """
    output_dir = pathlib.Path(output_dir)
    context = context or {}

    try:
        cookiecutter(
            template,
            extra_context=context,
            output_dir=output_dir,
            no_input=True,
            overwrite_if_exists=clobber,
        )
    except OutputDirExistsException as err:
        raise OutputDirExistsError(", ".join(err.args))

    name = context["plugin_name"]

    # path = os.path.join(output_dir, "pymt_{}".format(context["plugin_name"]))
    # if not os.path.isdir(path):
    path = output_dir / f"pymt_{name}"
    if not path.is_dir():
        raise RenderError("error creating {0}".format(path))

    return path


class StyleBlack:
    def __init__(self, filepath):
        with open(filepath, "r") as fp:
            try:
                new_contents = blk.format_file_contents(
                        fp.read(), fast=True, mode=blk.FileMode()
                    )
            except blk.NothingChanged:
                new_contents = None
        if new_contents:
            with open(filepath, "w") as fp:
                fp.write(new_contents)


def prettify_python(path_to_repo):
    path_to_repo = pathlib.Path(path_to_repo)
    with open(path_to_repo / "plugin.yaml") as fp:
        meta = yaml.safe_load(fp)
    module_name = "pymt_" + meta["plugin"]["name"]

    files_to_fix = [
        path_to_repo / "setup.py",
        path_to_repo / module_name / "bmi.py",
        path_to_repo / module_name / "__init__.py",
    ]

    for file_to_fix in files_to_fix:
        SortImports(file_to_fix, quiet=True)
        StyleBlack(file_to_fix)
