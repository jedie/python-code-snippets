#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
os.chdir("..") # go into PyLucid App root folder

from django.core import management

os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"
from PyLucid import settings

settings.DATABASE_ENGINE = "sqlite3"
settings.DATABASE_NAME = ":memory:"
settings.LANGUAGE_CODE = 'de'

print "init django, create tables...",
management.setup_environ(settings) # init django
management.syncdb(verbosity=0, interactive=False) # Create Tables
print "OK\n"

#______________________________________________________________________________
# Test:

from django.contrib.auth.models import User
from django import newforms as forms

UserForm = forms.form_for_model(User)
form = UserForm()
html_code = form.as_p()

print html_code