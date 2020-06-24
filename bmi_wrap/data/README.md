# Cookiecutter csdms-stack

[Cookiecutter](https://github.com/audreyr/cookiecutter) template for a wrapping bmi libraries

* GitHub repo: https://github.com/mcflugen/cookiecutter-bmi-wrap
* Free software: MIT license

## Quickstart

Install the latest Cookiecutter if you haven't installed it yet
(this requires Cookiecutter 1.4.0 or higher)::

    $ pip install -U cookiecutter

or

    $ conda install cookiecutter -c conda-forge

Generate a bmi-wrap extension module::

    $ cookiecutter https://github.com/mcflugen/bmi-stack.git

Then:
* Create a repo and put it there
* Add the repo to [Travis-CI](https://travis-ci.org)
* Run the Travis CLI command

      $ travis encrypt --add "ANACONDA_TOKEN=<token>"
