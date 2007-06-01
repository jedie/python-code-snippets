#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local django test with empty database.
"""

import os
os.chdir("../../") # go into PyLucid App root folder
#print os.getcwd()

from django.core import management

os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"
from PyLucid import settings

settings.DATABASE_ENGINE = "sqlite3"
settings.DATABASE_NAME = ":memory:"

#______________________________________________________________________________

print "setup the django environ and create the model tables...",
management.setup_environ(settings) # init django
management.syncdb(verbosity=0, interactive=False) # Create Tables
print "OK\n"

#______________________________________________________________________________
# Test:

from django.db.models import get_apps, get_models

for app in get_apps():
    print app.__name__
    for model in get_models(app):
        print model._meta.object_name

    print


#from PyLucid.models import Plugin, Markup, PagesInternal
#
#plugin = Plugin.objects.create()
#print "plugin ID:", plugin.id
#
#markup2 = Markup.objects.create(name="Test Markup")
#print markup2, type(markup2)
#print "markup2 ID:", markup2.id
#
#markup = Markup.objects.get(name="Test Markup")
#print markup, type(markup)
#print "markup2 ID:", markup.id
#
#internal_page = PagesInternal.objects.create(
#    name = "Test",
#    plugin = plugin, # The associated plugin
#    markup = markup,
#
#    content_html = "TEST content_html",
#    content_js = "TEST content_html",
#    content_css = "TEST content_html",
#    description = "Test description",
#)
#print internal_page