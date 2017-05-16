from unittest import TestCase


class TestUnicodeUtils(TestCase):

    def test_playaround(self):
        str_input = 'foo\u2127more'.decode('unicode_escape')
        print 'v: <%s>, type %s' % (input, type(str_input))
