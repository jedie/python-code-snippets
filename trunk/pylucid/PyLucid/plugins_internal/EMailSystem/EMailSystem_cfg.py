#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "send EMails to other PyLucid user."
__long_description__    = """With this Plugin you can send EMails to other
PyLucid users."""
__can_deinstall__ = True

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "user_list" : {
        "must_login"    : True,
        "must_admin"    : False,
#        "internal_page_info" : {
#            "description"       : "HTML form to edit a CMS Page",
#            "markup"            : None,
#        },
    },
}
