"""This module is for handling of command line arguments."""
import argparse


def setup():
    """This function sets up the arguments."""
    parser = argparse.ArgumentParser(
        description="RobinHood dashboard with basic authentication.")
    parser.add_argument("config",
                        help="File where configuration is located.",
                        type=str)
    args = parser.parse_args()
    return args
