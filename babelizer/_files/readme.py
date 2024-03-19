from jinja2 import Environment
from jinja2 import FileSystemLoader

from babelizer._datadir import get_datadir


def render(context):
    env = Environment(loader=FileSystemLoader(get_datadir()))
    template = env.get_template("{{cookiecutter.package_name}}/README.rst")

    return template.render(**context)
