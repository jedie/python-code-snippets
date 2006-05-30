#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

import cgi, time

from PyLucid.install.ObjectApp_Base import ObjectApp_Base





class update(ObjectApp_Base):
    "3. update"
    def update_db(self):
        "update db tables (PyLucid v0.6.x -> 0.7)"
        self._write_info()

        if not self._confirm("update db tables (PyLucid v0.6.x -> 0.7) ?"):
            # Abfrage wurde nicht bestätigt
            return

        # page_internals
        SQLcommand = "DROP TABLE $$pages_internal_category;"
        self._execute(
            "Delete obsolete 'pages_internal_category' table", SQLcommand
        )
        SQLcommand = (
            "CREATE TABLE $$pages_internal_css ("
            " name varchar(50) NOT NULL default '',"
            " plugin_id tinyint(4) default NULL,"
            " lastupdatetime datetime NOT NULL default '0000-00-00 00:00:00',"
            " lastupdateby int(11) NOT NULL default '0',"
            " content text NOT NULL,"
            " description text NOT NULL,"
            " PRIMARY KEY (name)"
            ") COMMENT='StyleSheets code storage for internal page';"
        )
        self._execute(
            "Add 'pages_internal_css' table (for StyleSheet code)", SQLcommand
        )
        SQLcommand = (
            "CREATE TABLE $$pages_internal_js ("
            " name varchar(50) NOT NULL default '',"
            " plugin_id tinyint(4) default NULL,"
            " lastupdatetime datetime NOT NULL default '0000-00-00 00:00:00',"
            " lastupdateby int(11) NOT NULL default '0',"
            " content text NOT NULL,"
            " description text NOT NULL,"
            " PRIMARY KEY (name)"
            ") COMMENT='JavaScript code storage for internal pages';"
        )
        self._execute(
            "Add 'pages_internal_js' table (for JavaScript code)", SQLcommand
        )

        # shortcut Spalte hinzufügen
        SQLcommand = (
            "ALTER TABLE $$pages"
            " ADD shortcut"
            " VARCHAR(50) NOT NULL"
            " AFTER name;"
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

        self._updateStyleTable()

        # plugindata Aufräumen
        SQLcommand = (
            "ALTER TABLE $$plugindata"
            " DROP parent_method_id,"
            " DROP CGI_laws,"
            " DROP get_CGI_data;"
        )
        self._execute(
            "Remove obsolete column in table plugindata",
            SQLcommand
        )

        # plugins anpassen
        SQLcommand = (
            "ALTER TABLE $$plugins"
            " CHANGE package_name package_name"
            " VARCHAR( 128 ) NOT NULL;"
        )
        self._execute(
            "change size of package_name column in plugins-table",
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

        self._db.commit()

    def _updateStyleTable(self):
        "Stylesheet-Tabelle mit Datumsfeldern versehen (PyLucid v0.6.x -> 0.7)"
        SQLcommand = (
            "ALTER TABLE $$styles"
            " ADD datetime DATETIME NOT NULL AFTER id,"
            " ADD lastupdatetime DATETIME NOT NULL AFTER datetime,"
            " ADD lastupdateby INT(11) NOT NULL AFTER lastupdatetime;"
        )
        self._execute("Add date-fields to stylesheets table", SQLcommand)

        defaultTime = self._tools.convert_time_to_sql(time.time())

        self.response.write("<h4>Update timestamps:</h4>")
        self.response.write("<pre>")
        styleList = self._db.get_style_list(["id","name"])
        for style in styleList:
            styleId = style["id"]
            styleName = style["name"]
            self.response.write(
                "update timestamp for '<strong>%s</strong>' ID:%s..." % (
                    styleName, styleId
                )
            )
            data = {
                "datetime": defaultTime,
                "lastupdatetime": defaultTime,
            }
            try:
                self._db.update_style(styleId, data)
            except Exception, e:
                self.response.write("Error: %s\n" % e)
            else:
                self.response.write("OK\n")

        self.response.write("</pre>")





















