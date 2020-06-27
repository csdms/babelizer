import pathlib

from cookiecutter.main import cookiecutter

from .errors import RenderError


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

    cookiecutter(
        template,
        extra_context=context,
        output_dir=output_dir,
        no_input=True,
        overwrite_if_exists=clobber,
    )

    name = context["plugin_name"]

    # path = os.path.join(output_dir, "pymt_{}".format(context["plugin_name"]))
    # if not os.path.isdir(path):
    path = output_dir / f"pymt_{name}"
    if not path.is_dir():
        raise RenderError("error creating {0}".format(path))

    return path
