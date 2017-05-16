from unittest import TestCase

from qtlayoutbuilder.lib.objectfinder import ObjectFinder


class Banana(object):
    """We look for instances of Bananas."""
    pass


class HasABanana(object):
    """
    We instantiate one of these to get an object that refers to a
    Banana via an attribute.
    """

    def __init__(self):
        self.my_banana = Banana()


class TestObjectFinder(TestCase):
    def test_search_for_objects_finding_local_variable(self):
        # We create a local variable 'my_banana' and then search for the object
        # it is pointing to.
        # noinspection PyUnusedLocal
        my_banana = Banana()
        finder = ObjectFinder([Banana, ])
        found = finder.find_objects('my_banana')
        self.assertEquals(len(found), 1)
        found_object = found[0]
        self.assertEquals(found_object.__class__, Banana)

    def test_search_for_objects_finding_instance_attribute(self):
        # We instantiate an 'HasABanana' and search for the Banana it
        # references.

        # We are NOT searching for the HasABanana instance. But for
        # the Banana it references by its 'my_banana' attribute.
        # noinspection PyUnusedLocal
        has_banana = HasABanana()
        finder = ObjectFinder([Banana, ])
        found = finder.find_objects('my_banana')
        self.assertEquals(len(found), 1)
        found_object = found[0]
        self.assertEquals(found_object.__class__, Banana)

    # noinspection PyUnusedLocal
    def test_search_finding_multiple(self):
        foo = HasABanana()
        bar = HasABanana()
        my_banana = Banana()
        wrong_name = Banana()
        finder = ObjectFinder([Banana, ])
        found = finder.find_objects('my_banana')
        self.assertEquals(len(found), 3)
