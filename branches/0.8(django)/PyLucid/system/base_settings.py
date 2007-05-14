
"""
PyLucid base settings

This things normaly does not have to be changed!
"""

PYLUCID_MODULE_PATHS = (
    "PyLucid/modules", "PyLucid/buildin_plugins", "PyLucid/plugins"
)

# Some special URL prefixes
INSTALL_URL_PREFIX = "_install"
COMMAND_URL_PREFIX = "_command"
ADMIN_URL_PREFIX = "_admin"

# The PyLucid install instrucion page:
INSTALL_HELP_URL = "http://www.pylucid.org/index.py/InstallPyLucid/"

# How are the DB initial data fixtures stored?
INSTALL_DATA_DIR = "PyLucid/fixtures"

# PyLucid Version String
PYLUCID_VERSION = (0,8,0,"alpha1")
PYLUCID_VERSION_STRING = "0.8.0alpha1"