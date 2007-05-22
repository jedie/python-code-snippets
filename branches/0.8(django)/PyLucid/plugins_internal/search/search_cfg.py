#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "The builtin search"
__long_description__ = """
A small search engine with rating for your CMS.
"""

#___________________________________________________________________________________________________
# Module-Manager Daten

plugin_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "input_form",
            "description"       : "The HTML form of the search module.",
            "template_engine"   : "string formatting",
            "markup"            : None
        },
    },
    "do_search"       : {
        "must_login"    : False,
        "must_admin"    : False,
    },
}
