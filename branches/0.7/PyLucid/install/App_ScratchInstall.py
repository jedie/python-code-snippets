#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Installation von PyLucid
"""

install_zipfileName = "PyLucid/PyLucid_SQL_install_data.zip"


import os, cgi, zipfile


from PyLucid.install.ObjectApp_Base import ObjectApp_Base

class install(ObjectApp_Base):
    "1. install PyLucid from scratch"
    def init_DB(self):
        "1. init Database tables"
        self._write_info()

        dbTablePrefix = self.request.preferences["dbTablePrefix"]

        d = SQL_dump(self.response, self._db, dbTablePrefix, simulation=True)
        try:
            d.openZipfile(install_zipfileName)
        except Exception, e:
            msg = "<h2>Can't open install-file:</h2><p>%s</p>" % e
            self.response.write(msg)
            return
        d.import_dump()
        #~ d.dump_data()

    def init_modules(self):
        "2. init basic Modules"
        self._write_info()

    def add_admin(self):
        "3. add a admin user"
        self._write_info()




class SQL_dump:
    """
    Klasse zum "verwalten" des SQL-install-Dumps
    """
    def __init__(self, response, db, dbTablePrefix, simulation=False):
        self.response = response
        #~ self.db = db
        self.db = None
        self.dbTablePrefix = dbTablePrefix
        self.simulation = simulation

        self.in_create_table = False
        self.in_insert = False

    def openZipfile(self, zipfileName):
        self.ziparchiv = zipfile.ZipFile(zipfileName, "r")

    def import_dump( self ):
        table_names = self.get_table_names()
        self.response.write("<pre>")
        for current_table in table_names:
            self.response.write("install DB table '%s'..." % current_table,)
            command = self.get_table_data(current_table)

            try:
                counter = self.execute_many(command)
            except Exception,e:
                self.response.write("ERROR: %s" % e)
            else:
                self.response.write("OK")

        self.response.write("</pre>")

    def _complete_prefix( self, data ):
        return data % { "table_prefix" : self.simulation }

    def install_tables( self, table_names ):
        """ Installiert nur die Tabellen mit angegebenen Namen """
        self.response.write("<pre>")
        reinit_tables = list(table_names)
        for current_table in table_names:
            self.response.write("re-initialisation DB table '%s':" % current_table)
            command = self.get_table_data(current_table)

            self.response.write(" - Drop table...",)
            try:
                status = self.execute(
                    "DROP TABLE `%s%s`;" % (config.dbconf["dbTablePrefix"],current_table)
                )
            except Exception, e:
                self.response.write("Error:", e)
            else:
                self.response.write("OK")

            self.response.write(" - recreate Table and insert values...",)
            try:
                counter = self.execute_many(command)
            except Exception,e:
                self.response.write("ERROR:", e)
                sys.exit()
            else:
                self.response.write("OK")

            reinit_tables.remove(current_table)
            print

        if reinit_tables != []:
            self.response.write("Error, Tables remaining:")
            self.response.write(table_names)
        self.response.write("</pre>")


    #__________________________________________________________________________________________
    # Zugriff auf ZIP-Datei

    def get_table_data(self, table_name):
        try:
            data = self.ziparchiv.read(table_name+".sql")
        except Exception, e:
            self.response.write("Can't get data for '%s': %s" % (table_name, e))
            sys.exit()

        return self._complete_prefix(data)

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

    #__________________________________________________________________________________________
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

    def execute( self, SQLcommand ):
        if self.simulation:
            SQLcommand = SQLcommand.encode("String_Escape")
            SQLcommand = cgi.escape(SQLcommand)
            self.response.write("%s\n" % SQLcommand)
            return
        #~ try:
        #~ self.response.write("execute:", SQLcommand)
        self.db.cursor.execute_unescaped(SQLcommand)
        #~ except Exception, e:
            #~ self.response.write("Error: '%s' in SQL-command:" % cgi.escape( str(e) ))
            #~ self.response.write("'%s'" % SQLcommand)
            #~ print
            #~ return False
        #~ else:
            #~ return True

    #__________________________________________________________________________________________

    def dump_data( self ):
        self.response.write("<h2>SQL Dump data:</h2>")
        print
        self.response.write("<pre>")
        for line in self.data.splitlines():
            self.response.write(cgi.escape( self._complete_prefix( line )  ))
        print "</pre>"



class DumpZipOpenError(Exception):
    """
    Dump als ZIP läßt sich nicht öffnen
    """
    pass