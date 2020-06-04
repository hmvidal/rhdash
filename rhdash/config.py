"""config"""
import sys
from json import JSONDecodeError
from json import load
from os.path import expanduser
from os.path import isfile
from os.path import join

DEFAULT_CONFIG_TYPE = "json"
DEFAULT_PATH = join(expanduser("~"), ".rhdash", "config")

TEMPLATE = {
    "dash": {
        "creds": {
            "user": "",
            "password": ""
        }
    },
    "robinhood": {
        "ema_days": []
    }
}

DEFAULT = {
    "dash": {
        "creds": {
            "user": "hello",
            "password": "world"
        }
    },
    "robinhood": {
        "ema_days": [10, 20, 50]
    }
}


def error(config_path):
    """General error handler when config not found."""
    print(f"Could not find {config_path} in config!")
    sys.exit(1)


def isvalid(config, template=TEMPLATE, parent=""):
    """Validates config file against template"""
    # def is_dict_or_list(item):
    #     return isinstance(item, (dict, list)) and len(item) > 0

    return isinstance(config, dict)

    # for element in template:
    #     if element not in config:
    #         error(".".join([parent, element]))
    #     if isinstance(template, dict) and is_dict_or_list(template[element]):
    #         assert isvalid(config[element], template[element],
    #                        ".".join([parent, element]))

    # return True


def fetch_config(args):
    """Get contents of config file at path, if it exists."""
    config = DEFAULT

    path = DEFAULT_PATH
    filetype = DEFAULT_CONFIG_TYPE

    config_file = args.config if args and args.config else ".".join(
        [path, filetype])

    if isfile(config_file):
        try:
            with open(config_file, 'r') as config_file:
                config = load(config_file)
                assert isvalid(config)
        except JSONDecodeError as e:
            print(f"Could not properly parse file '{path}'!")
            sys.exit(1)
    else:
        print(f"Config '{path}' is not a file!")
    return config
