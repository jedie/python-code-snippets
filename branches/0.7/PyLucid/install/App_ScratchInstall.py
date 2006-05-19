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

        formAdd = (
            '\t<label for="simulation">Simulation only:</label>\n'
            '\t<input id="simulation" name="simulation"'
            ' type="checkbox" value="yes" checked="checked" />\n'
            '\t<br />\n'
        )
        self._confirm("Init Database tables?", formAdd)

        simulation = self.request.form.get("simulation",False)

        d = SQL_dump(self.request, self.response, simulation)

        d.import_dump()
        #~ d.dump_data()

    #_________________________________________________________________________

    def init_modules(self):
        "2. init basic Modules"
        self._write_info()

        if not self._confirm("Init basic Modules?"):
            # Abfrage wurde nicht bestätigt
            return

    #_________________________________________________________________________

    def add_admin(self):
        "3. add a admin user"
        self._write_info()




