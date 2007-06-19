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
    :license: GNU GPL, see LICENSE for more details
"""


#_____________________________________________________________________________
# Path to the Plugins

INTERNAL_PLUGIN_PATH = "PyLucid/plugins_internal"
EXTERNAL_PLUGIN_PATH = "PyLucid/plugins_external"


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