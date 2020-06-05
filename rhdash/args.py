"""This module is for handling of command line arguments."""
from argparse import ArgumentParser
from argparse import SUPPRESS

from rhdash import __version__


def setup_args():
    """This function sets up the arguments."""
    parser = ArgumentParser(
        add_help=False,
        description="RobinHood dashboard with basic authentication.")

    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")

    setup_required(required)
    setup_optional(optional)

    args = parser.parse_args()
    return args


def setup_required(group):
    """Set up required arguments."""


def setup_optional(optional):
    """Set up optional arguments, including help."""
    optional.add_argument("-c",
                          "--config",
                          default=None,
                          help="File where configuration is located.",
                          type=str)

    optional.add_argument("-h",
                          "--help",
                          action="help",
                          default=SUPPRESS,
                          help="Show this help message and exit.")
    optional.add_argument("-p",
                          "--port",
                          default=8050,
                          type=int,
                          help="Port for default server.")
    optional.add_argument("--version",
                          action="version",
                          version=f"%(prog)s {__version__}",
                          help="Show program's version number and exit.")
