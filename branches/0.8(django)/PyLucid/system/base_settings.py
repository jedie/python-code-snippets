#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid base settings
    ~~~~~~~~~~~~~~~~~~~~~

    This things normaly does not have to be changed!
    You should only change your own settings.py

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


from django.contrib.auth.models import User
from PyLucid.models import JS_LoginData

old_set_password = User.set_password

def set_password(user, raw_password):
#    print "set_password() debug:", user, raw_password
    if user.id == None:
        # It is a new user. We must save the django user accound first to get a
        # existing user object with a ID and then the JS_LoginData can assign to it.
        user.save()

    # Save the password for the JS-SHA-Login:
    login_data, status = JS_LoginData.objects.get_or_create(user = user)
    login_data.set_password(raw_password)
    login_data.save()

    # Use the original method to set the django User password:
    old_set_password(user, raw_password)


# Make a hook into Django's default way to set a new User Password.
# Get the new raw_password and set the PyLucid password, too.
User.set_password = set_password

#_____________________________________________________________________________
# Path to the Plugins

PLUGIN_PATH = (
    {
        "type": "internal",
        "path": ("PyLucid", "plugins_internal"),
        "auto_install": True,
    },
    {
        "type": "external",
        "path": ("PyLucid", "plugins_external"),
        "auto_install": False,
    },
)
#INTERNAL_PLUGIN_PATH = "PyLucid/plugins_internal"
#EXTERNAL_PLUGIN_PATH = "PyLucid/plugins_external"


#_____________________________________________________________________________
# special URL prefixes

# Prefix for the install section
INSTALL_URL_PREFIX = "_install"
# Prefix for every command request
COMMAND_URL_PREFIX = "_command"
# Prefix to the django admin panel
ADMIN_URL_PREFIX = "_admin"


#_____________________________________________________________________________
# static URLs (used in Traceback messages)

# The PyLucid install instrucion page:
INSTALL_HELP_URL = "http://www.pylucid.org/index.py/InstallPyLucid/"


#_____________________________________________________________________________
# install DB Dump

# How are the DB initial database data stored?
INSTALL_DATA_DIR = 'PyLucid/db_dump_datadir'


#_____________________________________________________________________________
# chaching

PAGE_CACHE_PREFIX = "PyLucid_page_cache_"

#_____________________________________________________________________________
# Additional Data Tag

# A temporary inserted Tag for Stylesheet and JavaScript data from the internal
# pages. Added by PyLucid.plugins_internal.page_style and replaces in
# PyLucid.index._replace_add_data()
ADD_DATA_TAG = "<!-- additional_data -->"

#______________________________________________________________________________
# JS-SHA1-Login

INSTALL_COOKIE_NAME = "PyLucid_inst_auth"

# http://www.djangoproject.com/documentation/authentication/#other-authentication-sources
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "PyLucid.plugins_internal.auth.auth_backend.JS_SHA_Backend",
)