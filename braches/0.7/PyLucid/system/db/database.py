#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

"""
MySQLdb wrapper

Allgemeine Routinen für eine einfachere SQL Benutzung

Benötigt MySQLdb download unter:
http://sourceforge.net/projects/mysql-python/


Information
-----------
Generell wird keine Tracebacks abgefangen, das muß immer im eigentlichen
Programm erledigt werden!

Wie man die Klasse benutzt, kann man unten sehen ;)



ToDo
----
    * Es wird immer das paramstyle 'format' benutzt. Also mit %s escaped
"""

__version__="0.5"

__history__="""
v0.5
    - Aufteilung: SQL-Wrapper aufgegliedert
v0.4.1
    - Work-a-round für fehlendes lastrowid (s. PEP-0249) http://www.python-forum.de/viewtopic.php?p=28819#28819
v0.4
    - Verwendet nun einen eigenen Dict-Cursor ( http://pythonwiki.pocoo.org/Dict_Cursor )
    - Nur mit MySQLdb getestet!
v0.3
    - Wenn fetchall verwendet wird, werden in self.last_SQLcommand und self.last_SQL_values die
        letzten SQL-Aktionen festgehalten. Dies kann gut, für Fehlerausgaben verwendet werden.
v0.2
    - insert() filtert nun automatisch Keys im Daten-Dict raus, die nicht als Spalte in der Tabelle vorkommen
    - NEU: get_table_field_information() und get_table_fields()
v0.1.1
    - NEU: decode_sql_results() - Alle Ergebnisse eines SQL-Aufrufs encoden
v0.1.0
    - Umbau, nun kann man den table_prefix bei einer Methode auch mit angeben, um auch an Tabellen zu
        kommen, die anders anfangen als in der config.py festgelegt.
v0.0.9
    - in update() wird nun auch die where-value SQL-Escaped
v0.0.8
    - bei select() werden nun auch die select-values mit der SQLdb escaped
    - methode _make_values() gelöscht und einfach durch tuple() erstetzt ;)
v0.0.7
    - Statt query_fetch_row() wird der Cursor jetzt mit MySQLdb.cursors.DictCursor erstellt.
        Somit liefern alle Abfragen ein dict zurück! Das ganze funktioniert auch mit der uralten
        MySQLdb v0.9.1
    - DEL: query_fetch_row()
    - NEU: fetchall()
v0.0.6
    - NEU: query_fetch_row() und exist_table_name()
v0.0.5
    - Stellt über self.conn das Connection-Objekt zur verfügung
v0.0.4
    - Bugfixes
    - Debugfunktion eingefügt
    - Beispiel hinzugefügt
    - SQL "*"-select verbessert.
v0.0.3
    - Allgemeine SQL insert und update Funktion eingefügt
    - SQL-where-Parameter kann nun auch meherere Bedingungen haben
v0.0.2
    - Allgemeine select-SQL-Anweisung
    - Fehlerausgabe bei fehlerhaften SQL-Anfrage
v0.0.1
    - erste Release
"""

from __future__ import generators
import sys

try:
    from PyLucid.python_backports.utils import *
except ImportError:
    # Beim direkten Aufruf, zum Modul-Test!
    import sys
    sys.path.insert(0,"../")
    from PyLucid.python_backports.utils import *


debug = False


class Database(object):
    """
    Klasse, die nur allgemeine SQL-Funktionen beinhaltet
    """
    def __init__(self, request):
        self.request = request
        self.preferences = request.preferences

        # Zum speichern der letzten SQL-Statements (evtl. für Fehlerausgabe)
        self.last_SQLcommand = ""
        self.last_SQL_values = ()

        self.tableprefix = self.preferences["dbTablePrefix"]

        #~ try:
        self._make_connection()
        #~ except Exception, e:
            #~ error( "Can't connect to database!", e )

    def _make_connection(self):
        """
        Baut den connect mit dem Modul auf, welches in der config.py
        ausgewählt wurde.
        """
        self.dbTyp = self.preferences.get("dbTyp","MySQLdb")

        #_____________________________________________________________________________________________
        if self.dbTyp == "MySQLdb":
            try:
                import MySQLdb as dbapi
            except ImportError, e:
                msg  = "MySQLdb import error! Modul"
                msg += """ '<a href="http://sourceforge.net/projects/mysql-python/">python-mysqldb</a>' """
                msg += "not installed??? [%s]""" % e
                raise ImportError(msg)

            try:
                self.conn = WrappedConnection(
                    dbapi.connect(
                        host    = self.preferences["dbHost"],
                        user    = self.preferences["dbUserName"],
                        passwd  = self.preferences["dbPassword"],
                        db      = self.preferences["dbDatabaseName"],
                    ),
                    placeholder = '%s',
                    prefix = self.tableprefix
                )
            except Exception, e:
                msg = "Can't connect to DB"
                if e[1].startswith("Can't connect to local MySQL server through socket"):
                    msg += ", probably the server '%s' is wrong!" % self.preferences["dbHost"]
                msg += " [%s]" % e
                raise ConnectionError(msg)

            self.cursor = self.conn.cursor()

        #_____________________________________________________________________________________________
        elif self.dbTyp == "sqlite":
            try:
                from pysqlite2 import dbapi2 as dbapi
            except ImportError, e:
                msg  = "pysqlite import error! Modul"
                msg += """ '<a href="http://pysqlite.org">pysqlite-mysqldb</a>' """
                msg += "not installed???"""
                error( msg, e )

            self.conn   = dbapi.connect( "%s.db" % self.config.dbconf["dbDatabaseName"] )
            self.cursor = self.conn.cursor(factory=DictCursor)
        #_____________________________________________________________________________________________
        elif self.dbTyp == "odbc":
            try:
                import odbc
            except ImportError, e:
                msg  = "odbc import error! Mark Hammond's"
                msg += """ '<a href="http://starship.python.net/crew/mhammond/win32/">Win32all</a>' """
                msg += "not installed???"""
                error( msg, e )

            self.conn   = odbc.odbc()
                #~ host    = self.config.dbconf["dbHost"],
                #~ user    = self.config.dbconf["dbUserName"],
                #~ passwd  = self.config.dbconf["dbPassword"],
                #~ db      = self.config.dbconf["dbDatabaseName"],
            #~ )
            self.cursor = self.conn.cursor( odbc.cursors.DictCursor )
        #_____________________________________________________________________________________________
        elif self.dbTyp == "adodb":
            self.escapechar = "?"
            try:
                import adodbapi as dbapi
            except ImportError, e:
                msg  = "adodbapi import error!"
                msg += """ '<a href="http://adodbapi.sourceforge.net/">adodbapi</a>' """
                msg += "not installed???"""
                error( msg, e )

            DSN_info = (
                "DRIVER=SQL Server;"
                "SERVER=%s;"
                "DATABASE=%s;"
                "UID=%s;"
                "PASSWORD=%s;"
            ) % (
                dbconf["dbHost"],
                dbconf["dbDatabaseName"],
                dbconf["dbUserName"],
                dbconf["dbPassword"],
            )
            self.conn   = dbapi.connect(DSN_info)
            self.cursor = self.conn.cursor()
        else:
            raise ImportError("Unknow DB-Modul '%s' (look at config.py!):" % db_module)

    def close(self):
        "Connection schließen"
        self.conn.close()




class WrappedConnection(object):

    def __init__(self, cnx, placeholder, prefix=''):
        self.cnx = cnx
        self.placeholder = placeholder
        self.prefix = prefix

    def cursor(self):
        return IterableDictCursor(self.cnx, self.placeholder, self.prefix)

    def __getattr__(self, attr):
        """
        Attribute/Methoden des original Connection-Objekt durchreichen
        """
        return getattr(self.cnx, attr)



class IterableDictCursor(object):

    def __init__(self, cnx, placeholder, prefix):
        self._cursor = cnx.cursor()
        self._placeholder = placeholder
        self._prefix = prefix

        if not hasattr(self._cursor, "lastrowid"):
            # Patch, wenn die DB-API kein lastrowid (s. PEP-0249) hat
            if hasattr(self._cursor, 'insert_id'):
                # Ältere MySQLdb Versionen haben eine insert_id() Methode
                IterableDictCursor.lastrowid = property(IterableDictCursor._insert_id)
            else:
                # Manuelle Abfrage
                IterableDictCursor.lastrowid = property(IterableDictCursor._manual_lastrowid)

    def _insert_id(self):
        return self._cursor.insert_id()

    def _manual_lastrowid(self):
        return self._cursor.execute("SELECT LAST_INSERT_ID() AS id;")

    def __getattr__(self, attr):
        """
        Attribute/Methoden des original Cursor-Objekt durchreichen
        """
        return getattr(self._cursor, attr)

    def prepare_sql(self, sql):
        return sql.replace('$$', self._prefix)\
                  .replace('?', self._placeholder)

    def execute(self, sql, values=None):
        args = [self.prepare_sql(sql)]
        if values:
            args.append(values)
        self._cursor.execute(*tuple(args))

    def execute_unescaped(self, sql):
        """
        Only vor install_PyLucid...
        """
        self._cursor.execute(sql)

    def fetchone(self):
        row = self._cursor.fetchone()
        if not row:
            return ()
        result = {}
        for idx, col in enumerate(self._cursor.description):
            result[col[0]] = row[idx]
        return result

    def fetchall(self):
        rows = self._cursor.fetchall()
        result = []
        for row in rows:
            tmp = {}
            for idx, col in enumerate(self._cursor.description):
                tmp[col[0]] = row[idx]
            result.append(tmp)
        return result

    def __iter__(self):
        while True:
            row = self.fetchone()
            if not row:
                return
            yield row



class ConnectionError(Exception):
    pass


















