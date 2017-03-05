""" Test suite for BuildError. """

import unittest

""" Test suite for BuildError. """

import unittest


class TestSayHello(unittest.TestCase):
    """ Just a test case """

    def test_sum(self):
        """ Sum produces expected result """
        the_sum = 1 + 2
        self.assertEqual(the_sum, 5)

if __name__ == '__main__':
    unittest.main()

"""

from qtlayoutbuilder.builderror import BuildError


class TestSayHello(unittest.TestCase):

    def test_sum(self):
        the_sum = 1 + 2
        self.assertEqual(the_sum, 4)


class TestSayHelloAgain(unittest.TestCase):

    def test_foo(self):
        err = BuildError()
        err.push_message('foo')
        err.push_message('bar')
        formatted = err.format_as_single_string()
        self.assertEqual(formatted, 'wontbe')

if __name__ == '__main__':
    unittest.main()

    """
