#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = __long_description__ = (
    "FileStorage - Share you own files between computers"
    " Note: If you deinstall this Plugin all files lost!"
)

#___________________________________________________________________________________________________
# Module-Manager Daten

module_manager_data = {
    "lucidTag" : {
        "must_login"    : True,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "summary",
            "description"       : "summary",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "md5check" : {
        "must_login"    : True,
        "must_admin"    : False,
    },
    "download" : {
        "must_login"    : True,
        "must_admin"    : False,
    },
    "delete" : {
        "must_login"    : True,
        "must_admin"    : False,
    },
    "drop_table" : {
        "must_login"    : True,
        "must_admin"    : True,
    },
}
