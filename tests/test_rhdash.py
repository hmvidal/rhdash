"""Module dosctring"""
import unittest

from rhdash import __version__
from rhdash import rhdash
from tests import VERSION


class TestVersion(unittest.TestCase):
    """docstring"""
    def test_version(self):
        """Make sure tests and main are same version"""
        self.assertEqual(__version__, VERSION)


class TestRHDash(unittest.TestCase):
    """docstring"""
    def test_rhdash(self):
        """Make sure main returns"""
        self.assertTrue(rhdash.run())


if __name__ == "__main__":
    unittest.main()
