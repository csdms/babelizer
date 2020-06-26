import argparse
import textwrap

import yaml

from .. import __version__


def generate_parser():
    p = argparse.ArgumentParser(
        description="command-line tool for doing CSDMS related things.",
        fromfile_prefix_chars="@",
    )
    p.add_argument(
        "-V",
        "--version",
        action="version",
        version="csdms {0}".format(__version__),
        help="Show the csdms version number and exit.",
    )
    sub_parsers = p.add_subparsers(metavar="command", dest="cmd")
    sub_parsers.required = True

    configure_parser_wrap(sub_parsers)

    return p


class AppendKeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        getattr(namespace, "define_macros").append(values.split("="))


class SetDefaultsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        with open(values, "r") as fp:
            defaults = yaml.load(fp.read())
        parser.set_defaults(**defaults)


def configure_parser_wrap(sub_parsers=None):
    help = "Wrap a shared library that implements a BMI."

    example = textwrap.dedent(
        """

    Examples:

    csdms wrap --language=c libbmi.so

    """
    )
    if sub_parsers is None:
        p = argparse.ArgumentParser(
            description=help, fromfile_prefix_chars="@", epilog=example
        )
    else:
        p = sub_parsers.add_parser("wrap", help=help, description=help, epilog=example)
    p.add_argument("lib", help="library to wrap")
    p.add_argument("--output-dir", default=".", help="folder to dump files to")
    p.add_argument(
        "--clobber", action="store_true", help="clobber folder if it already exists"
    )
    p.add_argument("--prompt", action="store_true", help="prompt user for input")
    p.add_argument("--compile", action="store_true", help="build the extension module")
    p.add_argument("--name", help="name of the model")
    p.add_argument(
        "--language", help="language of the library", choices=["c", "c++"], default="c"
    )
    p.add_argument(
        "-l",
        "--libraries",
        dest="libraries",
        default=[],
        action="append",
        help="library names to link against",
    )
    p.add_argument(
        "-L",
        "--library-dirs",
        default=[],
        dest="library_dirs",
        action="append",
        help="directories to search for C/C++ libraries at link time",
    )
    p.add_argument(
        "-I",
        "--include-dirs",
        default=[],
        dest="include_dirs",
        action="append",
        help="directories to search for C/C++ header files",
    )
    p.add_argument(
        "--extra-compile-args",
        default=[],
        action="append",
        help="extra args to use when compiling",
    )
    p.add_argument(
        "-D",
        "--define-macros",
        default=[],
        # action=AppendKeyValueAction,
        action="append",
        help="macros to define explicitly",
    )
    p.add_argument(
        "-U",
        "--undef-macros",
        default=[],
        dest="undef_macros",
        action="append",
        help="macros to undefine explicitly",
    )
    p.add_argument("--module-name", default=None, help="name to use for the new module")
    p.add_argument("--class-name", default=None, help="name to use for the class")
    p.add_argument("--bmi-include", default=None, help="bmi include file")
    p.add_argument("--bmi-register", default=None, help="bmi registration function")
    from .main_wrap import execute

    p.set_defaults(func=execute)

    return p


def main():
    p = generate_parser()
    args = p.parse_args()

    args.func(args)
