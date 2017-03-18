from unittest import TestCase

from PySide.QtGui import QHBoxLayout

from qtlayoutbuilder.lib.keywords import starts_with_keyword, mark_all_keywords_found, instantiate_qobject_for


class TestKeywords(TestCase):

    def test_starts_with(self):

        # Not at very start
        keyword = starts_with_keyword(' HBOX and then other stuff')
        self.assertIsNone(keyword)

        # Not a keyword
        keyword = starts_with_keyword('BANANA and then other stuff')
        self.assertIsNone(keyword)

        # Properly formed
        keyword = starts_with_keyword('HBOX and then other stuff')
        self.assertEquals(keyword, 'HBOX')

        # All keywords
        for keyword in ['HBOX', 'VBOX', 'STACK', 'SPLIT', 'TAB']:
            found = starts_with_keyword(keyword)
            self.assertEquals(found, keyword)

    def test_mark_all_keywords_found(self):
        input = 'HBOX some other stuff VBOX'

        def callback(match):
            return 'XXX' + match.group()

        marked = mark_all_keywords_found(input, callback)
        self.assertEquals(marked, 'XXXHBOX some other stuff XXXVBOX')

    def test_instantiate_qobject_for(self):
        # Unrecognized keyword
        obj, err = instantiate_qobject_for('illegal keyword')
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue(
            'Cannot instantiate your QObject because this keyword is not recognized: <illegal keyword>' in msg)

        # Proper use
        obj, err = instantiate_qobject_for('HBOX')
        self.assertIsNone(err)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.__class__, QHBoxLayout)

