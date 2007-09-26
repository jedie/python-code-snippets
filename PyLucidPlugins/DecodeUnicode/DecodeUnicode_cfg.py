#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = __long_description__ = (
    "Unicode char table"
)

#___________________________________________________________________________________________________
# Module-Manager Daten

plugin_manager_data = {
    "lucidTag"  : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "select",
            "description"       : "select a unicode block range",
            "markup"            : None
        },
    },
    "display"   : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "display",
            "description"       : "display a unicode block range",
            "markup"            : None
        },
    },
}
