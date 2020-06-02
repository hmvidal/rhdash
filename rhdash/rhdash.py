"""Module dosctring"""
from rhdash.app import create_app
from rhdash.args import setup_args


def run_with(arguments):
    """Main entrypoint."""
    if arguments:
        app = create_app(arguments)
        app.run_server()
        return True

    return False


def run():
    arguments = setup_args()
    run_with(arguments)


if __name__ == "__main__":
    run()
