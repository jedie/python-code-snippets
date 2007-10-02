#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "The presentation plugin"
__long_description__    = __description__

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "menu" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "back_and_forth_links" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "nav_links",
            "description"       : "back and forth navigation links",
            "markup"            : None
        },
    }
}
