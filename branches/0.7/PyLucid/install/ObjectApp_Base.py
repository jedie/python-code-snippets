#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
BasisMethoden für alle Install-App-Bereiche

SQL_dump Klasse zum "verwalten" des SQL-install-Dumps
"""


install_zipfileName = "PyLucid/PyLucid_SQL_install_data.zip"


# Imports für ObjectApp_Base-Klasse
import inspect, sys, posixpath

# Imports für SQL_dump-Klasse:
import os, sys, cgi, zipfile


class ObjectApp_Base(object):
    """ Basisklasse von der jede ObjApp-Klasse ableitet """

    def _get_module_admin(self):
        from PyLucid.modules import module_admin

        module_admin = module_admin.module_admin(self.request, self.response)

        return module_admin


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

    #_________________________________________________________________________

    def _write_info(self):
        try:
            stack_info = inspect.stack()
            #~ self.response.echo(stack_info)
            stack_info = stack_info[1]
            attr_name = stack_info[3]
            info = getattr(self, attr_name).__doc__
        except:
            info = self.request.environ['PATH_INFO']

        self.response.write("<h3>%s</h3>" % info)

        self._write_backlink()

    def _write_backlink(self):
        url = posixpath.join(
            self._environ["SCRIPT_ROOT"], self._preferences["installURLprefix"]
        )
        self.response.write('<p><a href="%s">menu</a></p>' % url)

    def _confirm(self, txt, formAdd=""):
        """
        Automatische Bestätigung
        """
        if self.request.form.has_key("confirm"):
            # confirm-POST-Form wurde schon bestätigt
            return True

        self.response.write("<h4>%s</h4>\n" % txt)
        form = (
            '<form name="confirm" method="post" action="%s">\n'
            '%s'
            '\t<input type="submit" value="confirm" name="confirm" />\n'
            '</form>\n'
        ) % (self._URLs["current_action"], formAdd)
        self.response.write(form)

        # Es soll erst weiter gehen, wenn das Formular bestätigt wurde:
        sys.exit(0)

    #_________________________________________________________________________
    ## Sub-Action

    def _autoSubAction(self, actionName):
        if actionName == None:
            return

        if not isinstance(actionName, basestring):
            self.response.write("TypeError!")
            return

        if not hasattr(self, actionName):
            self.response.write("Error: %s not exists!" % actionName)
            return

        action = getattr(self, actionName)
        action()

    def _write_subactionmenu(self, subactions):
        self.response.write("<ul>\n")
        for action in subactions:
            if not hasattr(self, action):
                self.response.write("Error: %s not exists!" % action)
                continue

            name = self._niceActionName(action)
            txt = (
                '\t<li>'
                '<a href="%(url)s/%(action)s">%(name)s</a>'
                '</li>\n'
            ) % {
                "url": self._URLs["current_action"],
                "action": action,
                "name": name,
            }
            self.response.write(txt)
        self.response.write("</ul>\n")

    def _niceActionName(self, actionName):
        actionName = actionName.strip("_")
        actionName = actionName.replace("_", " ")
        return actionName











#_____________________________________________________________________________




class SQL_dump:
    """
    Klasse zum "verwalten" des SQL-install-Dumps
    """
    def __init__(self, request, response, simulation=False):
        self.response = response
        self.simulation = simulation

        self.db = request.db

        self.in_create_table = False
        self.in_insert = False

        try:
            self.ziparchiv = zipfile.ZipFile(install_zipfileName, "r")
        except (IOError, zipfile.BadZipfile), e:
            msg = (
                "<h2>Can't open install-file:</h2>\n"
                "<h4>%s - %s</h4>\n"
            ) % (sys.exc_info()[0], e)
            self.response.write(msg)
            sys.exit(1)

    def import_dump( self ):
        table_names = self.get_table_names()
        self.response.write("<pre>")
        for current_table in table_names:
            self.response.write(
                "install DB table '<strong>%s</strong>'..." % current_table
            )
            if self.simulation:
                self.response.write("\n<code>\n")

            command = self.get_table_data(current_table)

            try:
                counter = self.execute_many(command)
            except Exception,e:
                self.response.write("<strong>ERROR: %s</strong>" % e)
            else:
                if self.simulation:
                    self.response.write("</code>\n")
                else:
                    self.response.write("OK")

        self.response.write("</pre>")

    def install_tables(self, table_names):
        """ Installiert nur die Tabellen mit angegebenen Namen """
        self.response.write("<pre>")
        reinit_tables = list(table_names)
        for current_table in table_names:
            self.response.write("re-initialisation DB table '<strong>%s</strong>':\n" % current_table)
            command = self.get_table_data(current_table)

            self.response.write(" - Drop table...",)
            if self.simulation:
                self.response.write("\n<code>\n")
            try:
                status = self.execute("DROP TABLE `$$%s`;" % current_table)
            except Exception, e:
                self.response.write("Error: %s\n" % e)
            else:
                if self.simulation:
                    self.response.write("</code>\n")
                else:
                    self.response.write("OK\n")

            self.response.write(" - recreate Table and insert values...",)
            if self.simulation:
                self.response.write("\n<code>\n")
            try:
                counter = self.execute_many(command)
            except Exception,e:
                self.response.write("ERROR: %s\n" % e)
                sys.exit()
            else:
                if self.simulation:
                    self.response.write("</code>\n")
                else:
                    self.response.write("OK\n")

            reinit_tables.remove(current_table)
            self.response.write("\n")

        if reinit_tables != []:
            self.response.write("Error, Tables remaining:")
            self.response.write(table_names)
        self.response.write("</pre>")


    #_________________________________________________________________________
    # Zugriff auf ZIP-Datei

    def get_table_data(self, table_name):
        try:
            return self.ziparchiv.read(table_name+".sql")
        except Exception, e:
            self.response.write("Can't get data for '%s': %s" % (table_name, e))
            sys.exit()

    def get_table_names(self):
        """
        Die Tabellen namen sind die Dateinamen, außer info.txt
        """
        table_names = []
        for fileinfo in self.ziparchiv.infolist():
            if fileinfo.filename.endswith("/"):
                # Ist ein Verzeichniss
                continue
            filename = fileinfo.filename
            if filename == "info.txt":
                continue
            filename = os.path.splitext(filename)[0]
            table_names.append(filename)
        table_names.sort()
        return table_names

    #_________________________________________________________________________
    # SQL

    def execute_many(self, command):
        """
        In der Install-Data-Datei sind in jeder Zeile ein SQL-Kommando,
        diese werden nach einander ausgeführt
        """
        counter = 0
        for line in command.split("\n"):
            if line=="": # Leere Zeilen überspringen
                continue
            self.execute(line)
            counter += 1
        return counter

    def execute(self, SQLcommand):
        SQLcommand = SQLcommand % {"table_prefix":"$$"} #FIXME
        if self.simulation:
            SQLcommand = str(SQLcommand) # Unicode wandeln
            SQLcommand = SQLcommand.encode("String_Escape")
            SQLcommand = cgi.escape(SQLcommand)
            self.response.write("%s\n" % SQLcommand)
            return

        try:
            self.db.cursor.execute(SQLcommand)
        except Exception, e:
            self.response.write(
                "Error: '%s' in SQL-command:" % cgi.escape(str(e))
            )
            return False
        else:
            return True

    #_________________________________________________________________________

    def dump_data( self ):
        self.response.write("<h2>SQL Dump data:</h2>")
        print
        self.response.write("<pre>")
        for line in self.data.splitlines():
            self.response.write(cgi.escape(line))
        print "</pre>"







