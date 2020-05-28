"""Module dosctring"""
from rhdash.args import setup
from rhdash.config import fetch


def run():
    """Function docstring"""
    args = setup()
    if args:
        config = fetch(args.config)
        return True
    return False


if __name__ == "__main__":
    run()
