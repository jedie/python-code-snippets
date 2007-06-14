#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local page shortcut test with a full init PyLucid environment.
"""

from setup_environment import setup
setup(
    path_info=False, extra_verbose=False,
    syncdb=True, insert_dump=True
)

#______________________________________________________________________________
# Test:

from PyLucid.models import Page

def verbose_save(page, shortcut):
    print "source......: '%s'" % page.shortcut
    page.shortcut = shortcut
    page.save()
    print "after save..: '%s'" % page.shortcut

# get the first page
page = Page.objects.all()[0]

print
print "change the source sortcut"
new_shortcut = "A_New_ShortCut"
verbose_save(page, new_shortcut)
assert page.shortcut == new_shortcut


print
print "Test the non-ASCII stripting"
verbose_save(page, "--=[Short cut test]=--")
assert page.shortcut == "ShortCutTest"


print
print "No empty shortcut allowed"
verbose_save(page, "")
assert page.shortcut != ""

print
print "Unique Test"
test = "UniqueShortCutTest"
verbose_save(page, test)
page2 = Page.objects.all()[1] # Get the second page
verbose_save(page2, test)
assert page.shortcut != page2.shortcut