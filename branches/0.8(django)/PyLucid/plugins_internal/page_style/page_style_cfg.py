#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "Stylesheet module"
__long_description__ = """Puts the Stylesheet into the CMS page."""
__can_deinstall__ = False

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "print_current_style" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "sendStyle" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
}
