#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

import cgi


from PyLucid.system.exceptions import *


from PyLucid.install.ObjectApp_Base import ObjectApp_Base
from PyLucid.install.ObjectApp_Base import SQL_dump


class LowLevelAdmin(ObjectApp_Base):
    "2. low level Admin"
    def rebuildShortcuts(self):
        "Rebuild all shortcuts"
        self.response.write("<h4>Create shortcut's from pages names:</h4>\n")
        self.response.write("<pre>\n")
        result = self._db.select(
            select_items    = ["id","name","title"],
            from_table      = "pages",
        )
        nameList = []
        for line in result:
            id = line["id"]
            name = line["name"]
            if name=="" or name==None:
                name = line["title"]

            self.response.write("id %-3s: %-30s ->" % (id,cgi.escape(name)))

            shortcut = self._tools.getUniqueShortcut(name, nameList)
            nameList.append(shortcut)

            self.response.write("%-30s" % shortcut)

            self.response.write("--- update in db:")

            try:
                self._db.update(
                    table   = "pages",
                    data    = {"shortcut": shortcut},
                    where   = ("id",id)
                )
            except Exception, e:
                self.response.write("ERROR: %s" % e)
            else:
                self.response.write("OK")

            self.response.write("\n")
        self.response.write("</pre>\n")

    #_________________________________________________________________________

    def module_admin(self, sub_action=None, *info):
        "Module/Plugin Administration"
        #~ self._write_info()
        self._write_backlink()

        self.response.write("sub_action: %s\n" % sub_action)
        self.response.write("sinfo: %s\n" % str(info))

        #~ sub_action = ""

        module_admin = self._get_module_admin()

        if sub_action == "install":
            self.request.db.commit()
            package_name = ".".join(info[:-1])
            module_name = info[-1]
            try:
                module_admin.install(package_name, module_name)
            except IntegrityError, e:
                self.response.write("DB Error: %s\n" % e)
                self.request.db.rollback()
                self.response.write("(execute DB rollback)")
            except KeyError, e:
                self.response.write("KeyError: %s" % e)
            else:
                self.request.db.commit()
            return
        elif sub_action == "deinstall":
            try:
                module_admin.deinstall(info[0])
            except IntegrityError, e:
                self.response.write("DB Error: %s\n" % e)
                self.request.db.rollback()
                self.response.write("(execute DB rollback)")
            except KeyError, e:
                self.response.write("KeyError: %s" % e)
            else:
                self.request.db.commit()
            return
        elif sub_action == "reinit":
            try:
                module_admin.reinit(info[0])
            except IntegrityError, e:
                self.response.write("DB Error: %s\n" % e)
                self.request.db.rollback()
                self.response.write("(execute DB rollback)")
            except KeyError, e:
                self.response.write("KeyError: %s" % e)
            else:
                self.request.db.commit()
            return
        elif sub_action == "activate":
            try:
                module_admin.activate(info[0])
            except KeyError, e:
                self.response.write("KeyError: %s" % e)
        elif sub_action == "deactivate":
            try:
                module_admin.deactivate(info[0])
            except KeyError, e:
                self.response.write("KeyError: %s" % e)
        elif sub_action == "module_admin_info":
            self.module_admin_info()
            return
        elif sub_action == "administation_menu":
            self._write_backlink()
        elif sub_action == "init_modules":
            self.print_backlink()
            if self.CGIdata.get("confirm","no") == "yes":
                module_admin = self._get_module_admin()
                module_admin.first_time_install_confirmed()
            self._write_backlink()
            return

        module_admin.administation_menu()

    #_________________________________________________________________________

    def re_init(self):
        "partially re-initialisation DB tables"
        self._write_info()

        simulation = self.request.form.get("simulation",False)
        d = SQL_dump(self.request, self.response, simulation)

        selectedTables = self.request.form.getlist("tablename")
        if selectedTables!=[]:
            # Forumlar wurde abgeschickt
            d.install_tables(selectedTables)
            return

        txt = (
            '<form action="%s" method="post">\n'
            '<p>Which tables reset to defaults:</p>\n'
        ) % self._URLs["current_action"]
        self.response.write(txt)

        for name in d.get_table_names():
            txt = (
                '<input type="checkbox" id="%(name)s" name="tablename" value="%(name)s">'
                '<label for="%(name)s">%(name)s</label><br />\n'
            ) % {"name": name}
            self.response.write(txt)

        self.response.write(
            '<h4><strong>WARNING:</strong> The specified tables lost all Data!</h4>\n'
            '<label for="simulation">Simulation only:</label>\n'
            '<input id="simulation" name="simulation"'
            ' type="checkbox" value="yes" checked="checked" />\n'
            '<br />\n'
            '<input type="submit" value="reinit" name="reinit" />\n'
            '</form>\n'
        )








