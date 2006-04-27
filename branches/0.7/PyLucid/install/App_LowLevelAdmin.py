#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

from PyLucid.install.ObjectApp_Base import ObjectApp_Base

class LowLevelAdmin(ObjectApp_Base):
    "2. low level Admin"
    def module_admin(self):
        "Module/Plugin Administration"
        #~ self._write_info()
        self._write_backlink()

        module_admin = self._get_module_admin()

        sub_action = self.request.GET.get("sub_action", None)

        if sub_action == "install":
            try:
                module_admin.install(self.request.GET["package"], self.request.GET["module_name"])
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
                module_admin.deinstall(self.request.GET["id"])
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
                module_admin.reinit(self.request.GET["id"])
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
                module_admin.activate(self.request.GET["id"])
            except KeyError, e:
                self.response.write("KeyError: %s" % e)
        elif sub_action == "deactivate":
            try:
                module_admin.deactivate(self.request.GET["id"])
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