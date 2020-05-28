"""Module dosctring"""
from rhdash.args import setup


def run():
    """Function docstring"""
    args = setup()
    if args:
        return True
    return False


if __name__ == "__main__":
    run()
