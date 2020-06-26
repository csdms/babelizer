#! /usr/bin/env python
import os

from scripting.contexts import cd
from scripting.unix import system

from .. import __version__
from ..wrap import render


def get_library_name(path):
    fname, _ = os.path.splitext(os.path.basename(path))
    if fname.startswith("lib"):
        fname = fname[3:]

    return fname


def append_if_missing(item, items=None):
    items = items or []
    if item not in items:
        return items + [item]
    return items


def pop_if_none(context):
    for arg, value in context.items():
        if value is None:
            context.pop(arg)
    return context


def join_lists(context, delim=" "):
    for arg, value in context.items():
        if isinstance(value, list):
            try:
                context[arg] = ",".join(value)
            except TypeError:
                pass
    return context


def execute(args):
    context = args.__dict__

    context["libraries"] = append_if_missing(
        get_library_name(args.lib), items=args.libraries
    )

    pop_if_none(context)
    join_lists(context, delim=",")

    path = render(
        args.language,
        context,
        output_dir=args.output_dir,
        overwrite_if_exists=args.clobber,
    )
    if args.compile:
        with cd(path):
            system(["python", "setup.py", "develop"])


def main():
    import argparse
    from .main import configure_parser_wrap

    p = configure_parser_wrap()

    args = p.parse_args()

    args.func(args)
