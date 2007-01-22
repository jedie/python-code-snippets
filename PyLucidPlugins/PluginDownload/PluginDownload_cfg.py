#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben
__author__      = "Jens Diemer"
__url__         = "http://www.pylucid.org"
__description__ = __long_description__ = \
                    "Make a Download Page for all installed external Plugins"

#___________________________________________________________________________________________________
# Module-Manager Daten

module_manager_data = {
    "lucidFunction" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "lucidTag" 		: {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "PluginDownload",
            "description"       : "A list of all external plugins",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "download" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
}
