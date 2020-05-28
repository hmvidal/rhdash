"""This module is for handling of command line arguments."""
from argparse import ArgumentParser
from argparse import SUPPRESS


def setup_args():
    """This function sets up the arguments."""
    parser = ArgumentParser(
        add_help=False,
        description="RobinHood dashboard with basic authentication.")

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    setup_required(required)
    setup_optional(optional)

    args = parser.parse_args()
    return args


def setup_required(group):
    """Set up required arguments."""
    group.add_argument("-c",
                       "--config",
                       help="File where configuration is located.",
                       type=str,
                       required=True)


def setup_optional(optional):
    """Set up optional arguments, including help."""
    # Add back help
    optional.add_argument('-h',
                          '--help',
                          action='help',
                          default=SUPPRESS,
                          help='show this help message and exit')
