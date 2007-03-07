# Django settings for PyLucid project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'DatabaseName'             # Or path to database file if using sqlite3.
DATABASE_USER = 'UserName'             # Not used with sqlite3.
DATABASE_PASSWORD = 'Password'         # Not used with sqlite3.
DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
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

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'PyLucid.middlewares.page_msg.PageMessage',
    'PyLucid.middlewares.pagestats.PageStatsMiddleware',
)

ROOT_URLCONF = 'PyLucid.urls'

import os
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    os.getcwd(),
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
# PyLucid settings

TABLE_PREFIX = "pylucid_"

# Some special URL prefixes
INSTALL_URL_PREFIX = "_install"
COMMAND_URL_PREFIX = "_command"

# Install Password you should put this in the _install URL
INSTALL_PASS = "12345678"

# Enable the _install Python Web Shell Feature?
INSTALL_EVILEVAL = False

# PyLucid Version String
PYLUCID_VERSION = (0,8,0,"pre-alpha")
PYLUCID_VERSION_STRING = "0.8.0pre-alpha"