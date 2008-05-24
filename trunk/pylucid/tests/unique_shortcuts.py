#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Tests for Page shortcut creation.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007,2008 by PyLucid Team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import tests

from PyLucid.models import Page, Plugin

class Shortcuttest(tests.TestCase):
    """
    Tests for Page shortcut creation.
    """
    def setUp(self):
        """ Ensure that auto_shortcuts is false. """
        tests.change_preferences(
            plugin_name = "system_settings", auto_shortcuts = False
        )

        self.page = Page.objects.all()[0]

    def testChangeShortcut(self):
        """ Changing page shortcut """
        shortcuts = (("A_New_ShortCut","A_New_ShortCut"),
                     ("--=[Short cut test]=--","Short-cut-test"),
                     ("Short cut - test","Short-cut-test"))
        for shortcut_input, fixed_shortcut in shortcuts:
            self.page.shortcut = shortcut_input
            self.page.save()
            self.failUnlessEqual(self.page.shortcut, fixed_shortcut)

    def testEmptyShortcut(self):
        """ Empty shortcut is not allowed. """
        self.page.shortcut = ""
        self.page.save()
        self.failIfEqual(self.page.shortcut,"")

    def testShortcutUniqueness(self):
        self.page.shortcut = "UniqueShortCutTest"
        self.page.save()
        self.page2 = Page.objects.all()[1] # Get the second page
        self.page2.shortcut = "UniqueShortCutTest"
        self.page2.save()
        self.failIfEqual(self.page.shortcut,self.page2.shortcut)
        self.failUnlessEqual(self.page2.shortcut,"UniqueShortCutTest1")

    def testPageUpdate(self):
        """ Update a page only. (Shourtcut should not be changed!)"""
        new_shortcut = "UniqueShortCutTest"
        self.page.shortcut = new_shortcut
        self.page.save()
        self.failUnlessEqual(self.page.shortcut,new_shortcut)

        self.page.shortcut = new_shortcut
        self.page.save()
        self.failUnlessEqual(self.page.shortcut,new_shortcut)

    def testInsertPage(self):
        """ Insert a new page with a existing shortcut"""
        new_shortcut = "UniqueShortCutTest"
        self.page.shortcut = new_shortcut
        self.page.save()

        # For page.id = None look at:
        # http://www.djangoproject.com/documentation/db-api/#how-django-knows-to-update-vs-insert
        self.page.id = None # django recognizes page as new
        self.page.shortcut = new_shortcut
        self.page.save()
        self.failUnlessEqual(self.page.shortcut,new_shortcut+"1")

        self.page.id = None
        self.page.shortcut = new_shortcut
        self.page.save()
        self.failUnlessEqual(self.page.shortcut,new_shortcut+"2")

if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])