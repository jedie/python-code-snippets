#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

from PyLucid.system.exceptions import *

from PyLucid.install.ObjectApp_Base import ObjectApp_Base

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


    def re_init(self):
        "partially re-initialisation DB tables"
        self._write_info()