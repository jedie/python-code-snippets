#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

from PyLucid.install.ObjectApp_Base import ObjectApp_Base

class tests(ObjectApp_Base):
    "4. info / tests"
    def db_info(self):
        "DB connection Information"
        self._write_info()

        self.response.write("<pre>")
        for k,v in self.request.preferences.iteritems():
            if not k.startswith("db"):
                continue
            if k == "dbPassword":
                v = "***"
            self.response.write("%-20s: %s\n" % (k,v))
        self.response.write("</pre>")

    def module_admin_info(self):
        "Information about installed modules"
        self._write_info()

        self.PyLucid["URLs"]["current_action"] = "?action=module_admin&sub_action=module_admin_info"
        module_admin = self._get_module_admin()
        module_admin.debug_installed_modules_info()

    def path_info(self):
        "Path/URL check"
        self._write_info()