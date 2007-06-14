#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local test with a full init PyLucid environment
"""

import sys, os

def setup_path(chdir, path_info):
    if path_info:
        print "os.getcwd() 1:", os.getcwd()
    os.chdir(chdir) # go into PyLucid App root folder
    if path_info:
        print "os.getcwd() 2:", os.getcwd()
    sys.path.insert(0, os.getcwd())

def setup_django_environ():
    os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"
    from PyLucid import settings

    settings.DATABASE_ENGINE = "sqlite3"
    settings.DATABASE_NAME = ":memory:"

    print "- setup the django environ...",
    from django.core import management
    management.setup_environ(settings) # init django
    print "OK"

def make_syncdb():
    print "- create the model tables...",
    from django.core import management
    management.syncdb(verbosity=0, interactive=False) # Create Tables
    print "OK"

def make_insert_dump(extra_verbose):
    print "- insert the PyLucid install Dump...",
    if extra_verbose:
        print
    from PyLucid.install.install import DB_DumpFakeOptions
    from PyLucid.tools.db_dump import loaddb

    fake_options = DB_DumpFakeOptions()
    fake_options.verbose = extra_verbose
    loaddb(app_labels = [], format = "py", options = fake_options)



def setup(chdir="../../../", path_info=True, extra_verbose=True, syncdb=True,
                                                            insert_dump=True):
    """
    setup a test environment
    """
    print "Setup a local django environment for testing:"
    setup_path(chdir, path_info)
    setup_django_environ()
    if syncdb:
        make_syncdb()

    if insert_dump:
        make_insert_dump(extra_verbose)

    print "-"*80
    print



if __name__ == "__main__":
    print "Local Test:"
    setup()

    print "-"*80
    from PyLucid.models import Page
    print "Existing pages:"
    for page in Page.objects.all():
        print " *", page

    print "END"