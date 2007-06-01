#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local test with a full init PyLucid environment
"""

import sys, os
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

print "insert the PyLucid install Dump:"
from PyLucid.install.install import DB_DumpFakeOptions
from PyLucid.tools.db_dump import loaddb

fake_options = DB_DumpFakeOptions()
fake_options.verbose = False
loaddb(app_labels = [], format = "py", options = fake_options)
print

#______________________________________________________________________________

#print "install all base plugins:"
#from PyLucid.system import plugin_manager
#
#plugin_manager.install_internal_plugins()

#______________________________________________________________________________
# setup a faked PyLucid environment

from PyLucid.models import Page

class FakePageMsg(object):
    def __call__(self, *msg):
        for line in msg:
            print line

class FakeUser(object):
    def is_anonymous(self):
        return True

class FakeRequest(object):
    user = FakeUser()

fakeURLs = {
    "absoluteIndex": "/",
}

fake_context = {
    "request": FakeRequest(),
    "page_msg": FakePageMsg(),
    "URLs": fakeURLs,
    "PAGE": Page.objects.order_by('id')[1],
}
response = sys.stdout

#______________________________________________________________________________
# Test:

#from PyLucid.plugins_internal.main_menu.main_menu import main_menu
#
#main_menu(fake_context, response).lucidTag()

from pprint import pprint

from PyLucid.db.page import get_update_info
data = get_update_info(fake_context, 10)
for line in data:
    pprint(line)
    print



