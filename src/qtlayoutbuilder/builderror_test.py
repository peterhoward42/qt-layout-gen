from unittest import TestCase


class TestBuildError(TestCase):
    def test_push_message(self):
        self.fail()

    def test_format_as_single_string(self):
        self.faildoo()
