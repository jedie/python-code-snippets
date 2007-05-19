
"""
PyLucid base settings

This things normaly does not have to be changed!
"""

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "PyLucid.system.context_processors.static",
)

PYLUCID_MODULE_PATHS = ("PyLucid/plugins_internal", "PyLucid/plugins_external")

# Some special URL prefixes
INSTALL_URL_PREFIX = "_install"
COMMAND_URL_PREFIX = "_command"
ADMIN_URL_PREFIX = "_admin"

# The PyLucid install instrucion page:
INSTALL_HELP_URL = "http://www.pylucid.org/index.py/InstallPyLucid/"

# How are the DB initial data fixtures stored?
INSTALL_DATA_DIR = 'PyLucid/db_dump_datadir'

# Prefix for the PyLucid tables
TABLE_PREFIX = "pylucid_"