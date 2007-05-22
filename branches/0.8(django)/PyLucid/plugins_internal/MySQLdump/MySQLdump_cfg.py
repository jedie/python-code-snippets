#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__         = "Makes a MySQL dump for a backup"
__long_description__ = """
You can make a SQL dump from you DB. Also you can make a install-dump.
"""

#_____________________________________________________________________________
# Module-Manager Daten

plugin_manager_data = {
    "menu" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "MySQL dump Menu",
            "template_engine"   : "jinja",
            "markup"            : None
        },
    },
    "display_help"      : {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "display_dump"      : {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "display_command"   : {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "download_dump" : {
        "must_login"    : True,
        "must_admin"    : True,
        "direct_out"    : True,
    }
}

plugin_cfg = {
    "default_no_data" : ["log", "session_data", "object_cache"],
    "default character set": "utf8",
    "default compatible" : None,
    "list compatible" : [
        "ansi", "mysql323", "mysql40", "postgresql", "oracle",
        "mssql", "db2", "maxdb"
    ],
    "default parameters" : ["--compact"],
    "parameter examples" : [
        "--single-transaction", "--extended-insert", "--skip-opt"
    ],
}
