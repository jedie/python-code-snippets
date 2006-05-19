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
        "update db tables (PyLucid v0.6.x -> 0.7)"
        self._write_info()

        if not self._confirm("update db tables (PyLucid v0.6.x -> 0.7) ?"):
            # Abfrage wurde nicht bestätigt
            return

        # shortcut Spalte hinzufügen
        SQLcommand = (
            "ALTER TABLE $$pages "
            "ADD shortcut "
            "VARCHAR(50) NOT NULL "
            "AFTER name"
        )
        self._execute("Add 'shortcut' to pages table", SQLcommand)

        # shortcut auf unique setzten, falls das nicht schon der Fall ist
        table_keys = self._db.get_table_keys("pages")
        if not table_keys.has_key("shortcut"):
            SQLcommand = "ALTER TABLE $$pages ADD UNIQUE (shortcut)"
            self._execute(
                "set 'shortcut' in pages table to unique",
                SQLcommand
            )

        # plugindata Aufräumen
        SQLcommand = (
            "ALTER TABLE $$plugindata "
            "DROP parent_method_id, "
            "DROP CGI_laws, "
            "DROP get_CGI_data; "
        )
        self._execute(
            "Remove obsolete column in table plugindata",
            SQLcommand
        )

        # Verbesserung in der Tabelle, weil die Namen eindeutig sein sollen!
        table_keys = self._db.get_table_keys("template_engines")
        if not table_keys.has_key("name"):
            SQLcommand = "ALTER TABLE $$template_engines ADD UNIQUE (name)"
            self._execute(
                "set 'name' in template_engines table to unique",
                SQLcommand
            )

        # jinja eintragen
        self.response.write("<h4>insert 'jinja' template engine:</h4>\n")
        self.response.write("<pre>\n")
        try:
            self._db.insert(
                table = "template_engines",
                data  = {"name": "jinja"}
            )
        except Exception, e:
            self.response.write("ERROR: %s" % e)
        else:
            self.response.write("OK")
        self.response.write("</pre>\n")




