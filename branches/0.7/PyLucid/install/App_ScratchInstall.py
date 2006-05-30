#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Installation von PyLucid
"""




from PyLucid.install.ObjectApp_Base import ObjectApp_Base
from PyLucid.install.ObjectApp_Base import SQL_dump


class install(ObjectApp_Base):
    "1. install PyLucid from scratch"
    def init_DB(self):
        "1. init Database tables"
        self._write_info()

        self._confirm("Init Database tables?", simulationCheckbox=True)

        simulation = self.request.form.get("simulation",False)

        d = SQL_dump(self.request, self.response, simulation)

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

        self._page_msg(simulation)

        module_admin = self._get_module_admin()
        module_admin.first_time_install(simulation)

    #~ #_________________________________________________________________________

    #~ def add_admin(self):
        #~ "3. add a admin user"
        #~ self._write_info()

        #~ if not self._has_all_keys( self.CGIdata, ["username","email","pass1"] ):
            #~ self.db.print_internal_page("userhandling_add_user", {"url":"?add_admin"})
            #~ print "<strong>Note:</strong> Is admin checkbox ignored. Always create a admin account!"
            #~ return

        #~ if not self.CGIdata.has_key("realname"):
            #~ self.CGIdata["realname"] = None

        #~ usermanager = userhandling.userhandling(self.PyLucid)
        #~ try:
            #~ usermanager.add_user(
                #~ username    = self.CGIdata["username"],
                #~ email       = self.CGIdata["email"],
                #~ realname    = self.CGIdata["realname"],
                #~ admin       = 1
            #~ )
        #~ except KeyError, e:
            #~ print "CGIdata KeyError: '%s' not found! No user is added!" % e



