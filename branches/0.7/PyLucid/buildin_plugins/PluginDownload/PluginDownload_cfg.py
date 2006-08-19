#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben
__author__      = "Benjamin Weber + Jens Diemer"
__url__         = "http://blinx.tippsl.de"
__description__ = "Displays a random text of a Site in PyLucid."
__long_description__ = """
Displays a random text.
"""
__important_buildin__   = True

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "lucidFunction" : {
        "must_login"    : False,
        "must_admin"    : False,
        #"direct_out"    : True,
        #"sys_exit"      : True, # Damit ein sys.exit() auch wirklich fuktioniert
    },
    "download" : {
        "must_login"    : False,
        "must_admin"    : False,
        #"direct_out"    : True,
        #"sys_exit"      : True, # Damit ein sys.exit() auch wirklich fuktioniert
    }
}
