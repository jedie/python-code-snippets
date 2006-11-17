#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__              = "Alen Hopek"
__url__                 = "http://www.mactricks.de"
__description__         = "Organizes your E-Mail Adress Collection"
__long_description__ = """
You can organize all your E-Mail Adress Collection
"""

# __important_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

global_rights = {
        "must_login"    : False,
        "must_admin"    : False,
}

module_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    },

    "liste" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "email_auswahl_liste",
            "description"       : "List of E-Mail Adresses",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },

    "NewCategory" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "add_category",
            "description"       : "Add a new Category to E-Mail Management",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },

    "AddEmail" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "add_email",
            "description"       : "Add a new Mail Adress to E-Mail Management",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },

    "EditDataset" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "edit_dataset",
            "description"       : "Edit a selected Data Set",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },

    "DeleteDataset" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "delete_dataset",
            "description"       : "Delete a Mail Adress from Database",
            "template_engine"   : None,
            "markup"            : None
        },
    },

}