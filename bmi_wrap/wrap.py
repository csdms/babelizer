#! /usr/bin/env python
from __future__ import print_function

import os
import pkg_resources

from cookiecutter.main import cookiecutter


def render(language, context=None, output_dir=None, no_input=True,
           overwrite_if_exists=False):
    # template = pkg_resources.resource_filename(
    #     __name__, os.path.join('templates', language))
    template = pkg_resources.resource_filename(
        __name__, os.path.join('templates'))
    return cookiecutter(template, overwrite_if_exists=overwrite_if_exists,
                        no_input=no_input, output_dir=output_dir,
                        extra_context=context)
