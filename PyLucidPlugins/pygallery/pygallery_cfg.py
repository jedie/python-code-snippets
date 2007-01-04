#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = __long_description__ = (
    "PyGallery - A small picture gallery maker..."
)

#___________________________________________________________________________________________________
# Module-Manager Daten

module_manager_data = {
    "lucidTag" : {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "lucidFunction" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "setup" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "Setup all galleries",
            "template_engine"   : "jinja",
            "markup"            : None
        }
    },
    "gallery_config" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "Configure a existing gallery",
            "template_engine"   : "jinja",
            "markup"            : None
        }
    },
    "gallery" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "Default gallery Template",
            "template_engine"   : "jinja",
            "markup"            : None
        }
    },
    "make_thumbs" : {
        "must_login"    : True,
        "must_admin"    : True,
    },
}
plugin_cfg = {
    "dir_filter": ( # PyLucid-Verz. sollen ausgelassen werden.
            "colubrid", "jinja", "pygments", "PyLucid", "tests", "wsgiref"
    ),
    "galleries": {}
}