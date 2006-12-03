#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = __long_description__ = (
    "Execute Python code in PyLucid... This is *not* secure!!!"
)

#___________________________________________________________________________________________________
# Module-Manager Daten

global_rights = {
    "must_login"    : True,
    "must_admin"    : True,
}

module_manager_data = {
    "lucidTag" : global_rights,
    #~ "exec_codeline" : global_rights,
    "python" : global_rights,
    "shell": global_rights,
}
