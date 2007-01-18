#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Self PyLucid Documentation"
__long_description__ = """
Self PyLucid Documentation
"""

#_____________________________________________________________________________
# Module-Manager Daten

module_manager_data = {
    "lucidTag"  : {
        "must_login"        : False,
        "must_admin"        : False,
    },
    "menu"      : {
        "must_login"        : False,
        "must_admin"        : False,
    },
    "object_hierarchy": {
        "must_login"        : False,
        "must_admin"        : False,
        "menu_section"      : "system",
        "menu_description"  : "object hierarchy",
        "internal_page_info" : {
            "name"              : "object_select",
            "description"       : "Object select page",
            "template_engine"   : "jinja",
            "markup"            : None
        }
    },
}

plugin_cfg = {
    "object_names": ("request", "response"),
}
