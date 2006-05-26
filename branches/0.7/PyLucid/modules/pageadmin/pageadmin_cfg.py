#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
"""

#___________________________________________________________________________________________________
# Meta-Angaben

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "edit a CMS page"
__long_description__    = """Edit a normal CMS pages"""
__essential_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

global_rights = {
    "must_login"    : True,
    "must_admin"    : False,
}

module_manager_data = {
    "edit_page" : {
        "must_login"    : True,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "HTML form to edit a CMS Page",
            "template_engine"   : "string formatting",
            "markup"            : None,
        },
    },
    "new_page"          : global_rights,
    "delete_page"       : global_rights,
    "preview"           : global_rights,
    "save"              : global_rights,
    "encode_from_db"    : global_rights,

    "select_edit_page" : {
        "must_login"    : True,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "select a page to edit it",
            "template_engine"   : "string formatting",
            "markup"            : None,
        },
    },

    "select_del_page" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "select a page to delete it",
            "template_engine"   : "string formatting",
            "markup"            : None,
        },
    },

    "sequencing" : {
        "must_login"    : True,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "change the position of every page",
            "template_engine"   : "string formatting",
            "markup"            : None,
        },
    },
    "save_positions" : global_rights,
}
