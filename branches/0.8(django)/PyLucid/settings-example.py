#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Django settings for PyLucid project.

You must copy this file:
    settings-example.py -> settings.py
"""

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'PyLucid.db3'  # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#~ ADMIN_MEDIA_PREFIX = '/media/'
ADMIN_MEDIA_PREFIX = '/django/contrib/admin/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'a SECRET_KEY ?'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# After "syncdb" you must activate 'SessionMiddleware' and
# 'AuthenticationMiddleware'!!!
MIDDLEWARE_CLASSES = (
#    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'PyLucid.middlewares.pagestats.PageStatsMiddleware',
)

ROOT_URLCONF = 'PyLucid.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    # FIXME: Must that be an absolute path?
    "PyLucid/templates_django", "PyLucid/templates_PyLucid",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    "PyLucid",
)

#_____________________________________________________________________________
# import basic adjustments, witch don't have to be changed.
from system.base_settings import *

#_____________________________________________________________________________
# PyLucid settings - you can/should change!

"""
Note, you must edit MIDDLEWARE_CLASSES above, after installation!!!
"""

# Enable the _install Python Web Shell Feature?
INSTALL_EVILEVAL = False

# Install Password you should put this in the _install URL
#FIXME: ship a more save password
INSTALL_PASS = "12345678"
