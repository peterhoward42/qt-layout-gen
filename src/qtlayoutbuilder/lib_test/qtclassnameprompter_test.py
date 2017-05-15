from unittest import TestCase

from qtlayoutbuilder.lib.qtclassnameprompter import QtClassNamePrompter


class TestQtClassNamePrompter(TestCase):
    def test_basics(self):
        name = 'QHBoxlayout'  # Incorrect case for the letter 'l'
        suggestions = QtClassNamePrompter.suggest_names_similar_to_this(name)
        self.assertEqual(suggestions[0], 'QHBoxLayout')
