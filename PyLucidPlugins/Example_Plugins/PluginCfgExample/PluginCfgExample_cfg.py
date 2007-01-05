#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__              = "Jens Diemer"
__url__                 = "http://www.PyLucid.org"
__description__ = __long_description__ = "a small plugin_cfg Example"

#_____________________________________________________________________________
# Module-Manager Daten

module_manager_data = {
    "lucidTag" : {
        "must_login"    : True,
        "must_admin"    : False,
    },
}

##
## Das "plugin_cfg" kann jede Python Objekt Struktur sein, die mit pickle
## serialisiert werden kann.
##
## Hat das Plugin keine Einstellungsdaten, muß das plugin_cfg hier fehlen!
## Auch ein "plugin_cfg = None" wird als serialisiertes None in die Datenbank
## geschrieben ;)
##
plugin_cfg = {
    "data1": "foo",
    "data2": "bar",
}
