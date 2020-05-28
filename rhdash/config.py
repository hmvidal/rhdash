"""config"""
import sys
from json import JSONDecodeError
from json import load
from os.path import isfile


def fetch(path):
    """Get contents of config file at path, if it exists."""
    if isfile(path):
        try:
            with open(path, 'r') as config_file:
                config = load(config_file)
                return config
        except JSONDecodeError:
            print(f"Could not properly parse file '{path}'!")
            sys.exit(1)
    else:
        print(f"'{path}' is not a file!")
        sys.exit(1)
