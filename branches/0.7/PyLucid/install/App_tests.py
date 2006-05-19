#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

from PyLucid.install.ObjectApp_Base import ObjectApp_Base

class tests(ObjectApp_Base):
    "4. info / tests"
    def db_info(self, currentAction = None):
        "DB connection Information"
        self._write_info()

        subactions = [
            "_connect_information", "_show_grants",
            "_show_variables",
            "_show_engines", "_show_characterset"
        ]
        self._write_subactionmenu(subactions)

        self._autoSubAction(currentAction)

    def _connect_information(self):
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

        #~ self._execute_verbose("SELECT @@character set;")

    def _show_variables(self):
        self._execute_verbose("SHOW VARIABLES;")

    def _show_grants(self):
        self._execute_verbose("Available db storage engines", "SHOW GRANTS;")

    def _show_engines(self):
        self._execute_verbose("Available db storage engines", "SHOW ENGINES")

    def _show_characterset(self):
        self._execute_verbose("Available character set", "SHOW CHARACTER SET")

    #_________________________________________________________________________

    def table_info(self, sub_action=None, item=None):
        "DB Table info"
        self._write_info()

        self.response.write("<h3>table list</h3>")
        self.response.write(
            "<small>(only tables with prefix '%s')</small>" % \
                                                    self._db.tableprefix
        )
        self.response.write("<ul>")
        tableNameList = self._db.get_tables()
        for tableName in tableNameList:
            line = (
                '<li><a href="%(url)s/columns/%(name)s">%(name)s</a></li>'
            ) % {
                "url": self._URLs["current_action"],
                "name": tableName
            }
            self.response.write(line)

        self.response.write("</ul>")

        if sub_action == "columns":
            if item not in tableNameList:
                self.response.write("Error! '%s' not exists!" % item)
                return

            #~ self._execute_verbose("SHOW FULL TABLES;")
            #~ self._execute_verbose("SHOW TABLE STATUS FROM %s;" % item)
            self._execute_verbose("CHECK TABLE %s;" % item)
            self._execute_verbose("ANALYZE TABLE %s;" % item)
            self._execute_verbose("SHOW FULL COLUMNS FROM %s;" % item)
            self._execute_verbose("SHOW INDEX FROM %s;" % item)

            #~ SQLcommand = "DESCRIBE %s" % item
            #~ self._execute_verbose(SQLcommand)


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


    def _execute_verbose(self, title, SQLcommand=None):
        if SQLcommand == None:
            SQLcommand = title

        self.response.write("<h3>%s:</h3>\n" % title.rstrip(";"))

        try:
            self._db.cursor.execute(SQLcommand)
        except Exception, e:
            self.response.write("<pre>\n")
            self.response.write("execude ERROR: %s\n" % e)
            self.response.write("SQLcommand: %s\n" % SQLcommand)
            self.response.write("</pre>\n")
            return

        result = self._db.cursor.fetchall()

        # Daten als HTML-Tabelle ins response Obj. schreiben lassen:
        self._tools.writeDictListTable(result, self.response)










