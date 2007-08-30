"""
    PyLucid
    ~~~~~~~

    A Python based Content Management System
    written with the help of the powerful
    Webframework Django.


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.utils.version import get_svn_revision

svn_revision = get_svn_revision("PyLucid")

# PyLucid Version String
PYLUCID_VERSION = (0, 8, 0,"alpha3 " + svn_revision)
PYLUCID_VERSION_STRING = "0.8.0 alpha3 " + svn_revision


