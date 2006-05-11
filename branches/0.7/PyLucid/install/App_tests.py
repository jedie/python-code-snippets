#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

from PyLucid.install.ObjectApp_Base import ObjectApp_Base

class tests(ObjectApp_Base):
    "4. info / tests"
    def db_info(self, jau="jo"):
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
        self.response.write("<h3>db api info</h3>")
        self.response.write("<pre>")

        self.response.write("dbapi.......: ")
        try:
            self.response.write(
                "%s %s\n" % (self._db.dbapi.__name__, self._db.dbapi.__version__)
            )
        except Exception, e:
            self.response.write("(Error: %s)" % e)

        self.response.write("paramstyle..: %s\n" % self._db.paramstyle)
        self.response.write("placeholder.: %s\n" % self._db.placeholder)

        self.response.write("</pre>")
        self.response.write("<h3>table list</h3>")
        self.response.write(
            "<small>(only tables with prefix '%s')</small>" % \
                                                    self._db.tableprefix
        )
        self.response.write("<ul>")

        for tableName in self._db.get_tables():
            self.response.write("<li>%s</li>" % tableName)

        self.response.write("</ul>")


    def module_admin_info(self, module_id=None):
        "Information about installed modules"
        self._write_info()

        #~ self._URLs["current_action"] = self._URLs["base"]
        module_admin = self._get_module_admin()

        module_admin.debug_installed_modules_info(module_id)


    def path_check(self):
        "Path and URL check"
        self._write_info()

        self.response.write("<h4>generates automatically:</h4>")
        self.response.write("<pre>")
        for k,v in self._URLs.iteritems():
            self.response.write("%15s: %s\n" % (k,v))
        self.response.write("</pre>")
        self.response.write("<hr/>")










