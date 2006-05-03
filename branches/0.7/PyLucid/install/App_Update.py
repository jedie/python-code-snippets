#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

import cgi

from PyLucid.install.ObjectApp_Base import ObjectApp_Base





class update(ObjectApp_Base):
    "3. update"
    def update_db(self):
        "update pagenames-shorthands (PyLucid v0.x -> 0.7)"
        self._write_info()

        SQLcommand = (
            "ALTER TABLE $$pages "
            "ADD shortcut "
            "VARCHAR(50) NOT NULL "
            "AFTER name"
        )
        self._execute("Add 'shortcut' to pages table", SQLcommand)

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

        SQLcommand = "ALTER TABLE $$pages ADD UNIQUE (shortcut)"
        self._execute("set 'shortcut' to unique", SQLcommand)

    def _execute(self, title, SQLcommand):
        self.response.write("<h4>%s:</h4>\n" % title)
        self.response.write("<pre>\n")

        try:
            self._db.cursor.execute(SQLcommand)
        except Exception, e:
            self.response.write("ERROR: %s" % e)
        else:
            self.response.write("OK")

        self.response.write("</pre>\n")

