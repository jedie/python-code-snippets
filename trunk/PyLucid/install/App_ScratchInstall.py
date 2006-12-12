#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Installation von PyLucid


Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""

__version__= "$Rev:$"




from PyLucid.install.ObjectApp_Base import ObjectApp_Base
from PyLucid.install.SQLdump import SQLdump


class install(ObjectApp_Base):
    "1. install PyLucid from scratch"
    def init_DB(self):
        "1. init Database tables"
        self._write_info()

        self._confirm("Init Database tables?", simulationCheckbox=True)

        simulation = self.request.form.get("simulation",False)

        d = SQLdump(self.request, self.response, simulation)

        d.import_dump()
        #~ d.dump_data()

    #_________________________________________________________________________

    def init_modules(self):
        """
        2. init basic Modules

        Installiert die wichtisten Basis-Module

        1. Erstellt die Tabellen für den Module/Plugin-Manager
        2. installiert die Basic Module
        3. aktiviert die Module
        """
        self._write_info()

        self._confirm("Init all basic modules?")

        simulation = self.request.form.get("simulation",False)

        module_admin = self._get_module_admin()
        module_admin.first_time_install(simulation)

    #_________________________________________________________________________

    def add_admin(self):
        "3. add a admin user"
        self._write_info()

        from PyLucid.modules.userhandling import userhandling
        usermanager = userhandling.userhandling(self.request, self.response)
        #~ usermanager.add_user()
        usermanager.manage_user()



