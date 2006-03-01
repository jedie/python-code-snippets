#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

"""
Stellt die Verbindung zur DB her.
Bietet dabei einen DictCursor für alle SQL-DBs.

Links:
MySQLdb: http://sourceforge.net/projects/mysql-python/
PySQLite: http://www.initd.org/tracker/pysqlite/


Information
-----------
Generell wird keine Tracebacks abgefangen, das muß immer im eigentlichen
Programm erledigt werden!

Erwartet ein WSGI request-Objekt s. http://wsgiarea.pocoo.org/colubrid/




ToDo
----
    * Es wird immer das paramstyle 'format' benutzt. Also mit %s escaped
"""

__version__="0.6.1"

__history__="""
v0.6.1
    - encode_sql_results für unicode angepasst.
    - databasename global gemacht
    - bugfixes
v0.6
    - Einige Anpassungen für SQLite
    - Weil's portabler ist, database.py und SQL_wrapper.py zusammen gelegt.
    - self.fetchall umbenannt in process_statement
v0.5
    - Aufteilung: SQL-Wrapper aufgegliedert
v0.4.1
    - Work-a-round für fehlendes lastrowid
        (s. PEP-0249) http://www.python-forum.de/viewtopic.php?p=28819#28819
v0.4
    - Verwendet nun einen eigenen Dict-Cursor
        ( http://pythonwiki.pocoo.org/Dict_Cursor )
    - Nur mit MySQLdb getestet!
v0.3
    - Wenn fetchall verwendet wird, werden in self.last_SQLcommand und
        self.last_SQL_values die letzten SQL-Aktionen festgehalten. Dies kann
        gut, für Fehlerausgaben verwendet werden.
v0.2
    - insert() filtert nun automatisch Keys im Daten-Dict raus, die nicht als
        Spalte in der Tabelle vorkommen
    - NEU: get_table_field_information() und get_table_fields()
v0.1.1
    - NEU: decode_sql_results() - Alle Ergebnisse eines SQL-Aufrufs encoden
v0.1.0
    - Umbau, nun kann man den table_prefix bei einer Methode auch mit angeben,
        um auch an Tabellen zu kommen, die anders anfangen als in der
        config.py festgelegt.
v0.0.9
    - in update() wird nun auch die where-value SQL-Escaped
v0.0.8
    - bei select() werden nun auch die select-values mit der SQLdb escaped
    - methode _make_values() gelöscht und einfach durch tuple() erstetzt ;)
v0.0.7
    - Statt query_fetch_row() wird der Cursor jetzt mit
        MySQLdb.cursors.DictCursor erstellt. Somit liefern alle Abfragen ein
        dict zurück! Das ganze funktioniert auch mit der uralten
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


debug = False
#~ debug = True


class Database(object):
    """
    Klasse, die nur allgemeine SQL-Funktionen beinhaltet
    """
    def __init__(self, dbtyp, databasename, tableprefix="", host=None, \
        username=None, password=None):

        # Zum speichern der letzten SQL-Statements (evtl. für Fehlerausgabe)
        self.last_statement = None

        self.dbtyp = dbtyp
        self.databasename = databasename
        self.tableprefix = tableprefix

        #~ try:
        self._make_connection(host, username, password)
        #~ except Exception, e:
            #~ error( "Can't connect to database!", e )

    def _make_connection(self, host, username, password):
        """
        Baut connection zur DB auf.
        Stellt self.conn und self.cursor zur verfügung
        """

        #_____________________________________________________________________
        if self.dbtyp == "MySQLdb":
            try:
                import MySQLdb as dbapi
            except ImportError, e:
                msg  = "MySQLdb import error! Modul "
                msg += '<a href="http://sourceforge.net/projects/mysql-python/">'
                msg += 'python-mysqldb</a> not installed??? [%s]' % e
                raise ImportError(msg)

            self._setup_paramstyle(dbapi.paramstyle)

            try:
                self.conn = WrappedConnection(
                    dbapi.connect(
                        host    = host,
                        user    = username,
                        passwd  = password,
                        db      = self.databasename,
                    ),
                    placeholder = self.placeholder,
                    prefix = self.tableprefix
                )
            except Exception, e:
                msg = "Can't connect to DB"
                if e[1].startswith("Can't connect to local MySQL server through socket"):
                    msg += ", probably the server '%s' is wrong!" % host
                msg += " [%s]" % e
                raise ConnectionError(msg)

            self.cursor = self.conn.cursor()

        #_____________________________________________________________________
        elif self.dbtyp == "sqlite":
            try:
                from pysqlite2 import dbapi2 as dbapi
            except ImportError, e:
                msg  = "pysqlite import error! Modul "
                msg += '<a href="http://pysqlite.org">pysqlite-mysqldb</a>'
                msg += " not installed???"""
                error(msg, e)

            self._setup_paramstyle(dbapi.paramstyle)

            try:
                self.conn = WrappedConnection(
                    dbapi.connect(self.databasename),
                    placeholder = self.placeholder,
                    prefix = self.tableprefix
                )
            except Exception, e:
                import os
                msg = "Can't connect to SQLite-DB (%s)\n - " % e
                msg += "check the write rights on '%s'\n - " % os.getcwd()
                msg += "Databasename: '%s'" % self.databasename
                raise ConnectionError(msg)

            self.cursor = self.conn.cursor()
        #_____________________________________________________________________
        #~ elif self.dbtyp == "odbc":
            #~ try:
                #~ import odbc
            #~ except ImportError, e:
                #~ msg  = "odbc import error! Mark Hammond's "
                #~ msg += '<a href="http://starship.python.net/crew/mhammond/win32/">'
                #~ msg += 'Win32all</a> not installed???'
                #~ error( msg, e )

            #~ self.conn   = odbc.odbc()
                #~ host    = self.config.dbconf["dbHost"],
                #~ user    = self.config.dbconf["dbUserName"],
                #~ passwd  = self.config.dbconf["dbPassword"],
                #~ db      = databasename,
            #~ )
            #~ self.cursor = self.conn.cursor( odbc.cursors.DictCursor )
        #_____________________________________________________________________
        #~ elif self.dbtyp == "adodb":
            #~ self.escapechar = "?"
            #~ try:
                #~ import adodbapi as dbapi
            #~ except ImportError, e:
                #~ msg  = "adodbapi import error!"
                #~ msg += '<a href="http://adodbapi.sourceforge.net/">adodbapi</a>'
                #~ msg += "not installed???"""
                #~ error( msg, e )

            #~ DSN_info = (
                #~ "DRIVER=SQL Server;"
                #~ "SERVER=%s;"
                #~ "DATABASE=%s;"
                #~ "UID=%s;"
                #~ "PASSWORD=%s;"
            #~ ) % (
                #~ dbconf["dbHost"],
                #~ dbconf["dbDatabaseName"],
                #~ dbconf["dbUserName"],
                #~ dbconf["dbPassword"],
            #~ )
            #~ self.conn   = dbapi.connect(DSN_info)
            #~ self.cursor = self.conn.cursor()
        #~ else:
            #~ raise ImportError(
                #~ "Unknow DB-Modul '%s' (look at config.py!):" % db_module
            #~ )

    def commit(self):
        self.conn.commit()
    def rollback(self):
        self.conn.rollback()

    def _setup_paramstyle(self, paramstyle):
        """
        Setzt self.placeholder je nach paramstyle
        """
        self.paramstyle = paramstyle

        try:
            self.placeholder = {
                'qmark': '?',
                'format': '%s',
            }[paramstyle]
        except KeyError, e:
            msg  = "Error: %s\n --- " % e
            msg += "dbapi '%s' paramstyle '%s' not supportet!" % (
                self.dbtyp, paramstyle
            )
            raise KeyError(msg)

    def close(self):
        "Connection schließen"
        self.conn.close()



#_____________________________________________________________________________
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


#_____________________________________________________________________________
class IterableDictCursor(object):
    """
    -Bietet für alle DB-Engines einen Dict-Cursor
    -cursor.lastrowid für alle DB-Engines
    -curosr.last_statement beinhaltet immer den letzten execute
    """

    def __init__(self, cnx, placeholder, prefix):
        self._cursor = cnx.cursor()
        self._placeholder = placeholder
        self._prefix = prefix

        if not hasattr(self._cursor, "lastrowid"):
            # Patch, wenn die DB-API kein lastrowid (s. PEP-0249) hat
            if hasattr(self._cursor, 'insert_id'):
                # Ältere MySQLdb Versionen haben eine insert_id() Methode
                IterableDictCursor.lastrowid = property(
                    IterableDictCursor._insert_id
                )
            else:
                # Manuelle Abfrage
                IterableDictCursor.lastrowid = property(
                    IterableDictCursor._manual_lastrowid
                )

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

        self.last_statement = args

        try:
            self._cursor.execute(*tuple(args))
        except Exception, e:
            msg = "cursor.execute error: %s --- " % e
            msg += "\nargs: %s" % args
            raise Exception(msg)

    def execute_unescaped(self, sql):
        """
        execute without prepare_sql (replace prefix and placeholders)
        """
        self.last_statement = sql
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







#_____________________________________________________________________________
class SQL_wrapper(Database):
    """
    SQL-Statements Wrapper

    * Sammlung von Methoden für grundlegenden SQL-Statements:
        * SELECT
        * INSERT
        * UPDATE
        * DELETE
    * Zusätzlich ein paar Allgemeine Information Methoden.

    Nutzt ein filelike request-Objekt (WSGI) für Debugausgaben.
    Es geht auch sys.stdout :)
    """

    def __init__(self, request, *args, **kwargs):
        super(SQL_wrapper, self).__init__(*args, **kwargs)
        self.request = request

    def process_statement(self, SQLcommand, SQL_values = ()):
        """ kombiniert execute und fetchall """
        try:
            self.cursor.execute(SQLcommand, SQL_values)
        except Exception, e:
            msg  = "execute Error: %s\n --- " % e
            msg += "SQL-command: %s\n --- " % SQLcommand
            msg += "SQL-values: %s" % str(SQL_values)
            raise Exception(msg)

        try:
            result = self.cursor.fetchall()
        except Exception, e:
            raise Exception(
                "fetchall Error: %s --- SQL-command: %s --- SQL-values: %s" % (
                e, SQLcommand, SQL_values
                )
            )

        return result

    def insert(self, table, data, debug=False):
        """
        Vereinfachter Insert, per dict
        data ist ein Dict, wobei die SQL-Felder den Key-Namen im Dict
        entsprechen muss dabei werden Keys, die nicht
        in der Tabelle als Spalte vorkommt vorher rausgefiltert
        """
        #~ raise "test: %s" % self.databasename
        items  = data.keys()
        values = tuple(data.values())

        SQLcommand = "INSERT INTO $$%(table)s (%(items)s) VALUES (%(values)s);" % {
                "table"         : table,
                "items"         : ",".join(items),
                "values"        : ",".join([self.placeholder]*len(values))
            }

        result = self.process_statement(SQLcommand, values)
        if debug: self.debug_command("insert")
        return result

    def update(self, table, data, where, limit=False, debug=False):
        """
        Vereinfachte SQL-update Funktion
        """
        data_keys   = data.keys()

        values      = data.values()
        values.append(where[1])
        values      = tuple(values)

        set = ",".join(["%s=%s" % (i, self.placeholder) for i in data_keys])

        SQLcommand = "UPDATE $$%(table)s SET %(set)s WHERE %(where)s%(limit)s;" % {
                "table"     : table,
                "set"       : set,
                "where"     : "%s=%s" % (where[0], self.placeholder),
                "limit"     : self._make_limit(limit)
            }

        result = self.process_statement(SQLcommand, values)
        if debug: self.debug_command("update")
        return result


    def select(self, select_items, from_table, where=None, order=None, limit=None,
            maxrows=0, how=1, debug=False):
        """
        Allgemeine SQL-SELECT Anweisung
        where, order und limit sind optional

        where
        -----
        Die where Klausel ist ein wenig special.

        einfache where Klausel:
        where=("parent",0) ===> WHERE `parent`="0"

        mehrfache where Klausel:
        where=[("parent",0),("id",0)] ===> WHERE `parent`="0" and `id`="0"

        maxrows - Anzahl der zur���gegebenen Datens嵺e, =0 alle Datens嵺e
        how     - Form der zur���gegebenen Daten. =1 -> als Dict, =0 als Tuple
        """
        SQLcommand = "SELECT " + ",".join( select_items )
        SQLcommand += " FROM $$%s" % from_table

        values = []

        if where:
            where_string, values = self._make_where( where )
            SQLcommand += where_string

        if order:
            try:
                SQLcommand += " ORDER BY %s %s" % order
            except TypeError,e:
                raise TypeError(
                    "Error in db.select() ORDER statement (must be a tuple or List): %s" % e
                )

        SQLcommand += self._make_limit(limit)

        result = self.process_statement(SQLcommand, values)
        if debug: self.debug_command("select")
        return result

    def delete(self, table, where, limit=1, debug=False):
        """
        DELETE FROM table WHERE id=1 LIMIT 1
        """
        SQLcommand = "DELETE FROM $$%s" % table

        where_string, values = self._make_where(where)

        SQLcommand += where_string
        if not self.dbtyp == "sqlite":
            # sqlite hat kein LIMIT bei DELETE, sondern nur bei SELECT
            SQLcommand += self._make_limit(limit)
        SQLcommand += ";"

        result = self.process_statement(SQLcommand, values)
        if debug: self.debug_command("delete")
        return result

    #_________________________________________________________________________
    # Hilfsmethoden

    def _make_where(self, where):
        """
        Baut ein WHERE-Statemant und die passenden SQL-Values zusammen
        """
        if isinstance(where[0], str):
            # es ist nur eine where-Regel vorhanden.
            # Damit die folgenden Anweisungen auch gehen
            where = [ where ]

        where_string            = []
        SQL_parameters_values   = []

        for item in where:
            where_string.append("(%s=%s)" % (item[0], self.placeholder))
            SQL_parameters_values.append( item[1] )

        where_string = ' WHERE %s' % " and ".join(where_string)

        return where_string, tuple(SQL_parameters_values)

    def _make_limit(self, limit):
        """
        Baut den LIMIT Teil zusammen.
        """
        if not limit: return ""

        if isinstance(limit,(str,int)):
            return " LIMIT %s" % limit

        try:
            return " LIMIT %s,%s" % limit
        except TypeError,e:
            raise TypeError(
                "db Wrapper Error: LIMIT statement (must be a tuple or List): %s" % e
            )

    def cleanup_datadict(self, data, tablename):
        """
        Nicht vorhandene Tabellen-Spalten aus dem Daten-Dict löschen
        FIXME!
        """
        field_list = self.get_table_fields(tablename, debug)
        if debug:
            print "field_list for %s: %s" % (table, field_list)
        index = 0
        for key in list(data.keys()):
            if not key in field_list:
                del data[key]
            index += 1

    #_________________________________________________________________________

    def get_all_tables(self):
        """
        Liste aller Tabellennamen
        """
        if self.dbtyp == "mysql":
            return self.process_statement("SHOW TABLES")
        elif self.dbtyp == "sqlite":
            names = []
            for line in self.process_statement(
            "SELECT tbl_name FROM sqlite_master;"):
                if not line["tbl_name"] in names:
                    names.append(line["tbl_name"])
            return names

    def get_tables(self):
        """
        Liefert alle Tabellennamen die das self.tableprefix haben
        """
        tables = []
        for tablename in self.get_all_tables():
            if tablename.startswith(self.tableprefix):
                tables.append(tablename)
        return tables

    def get_table_field_information(self, table_name, debug=False):
        """
        Liefert "SHOW FIELDS", PRAGMA table_info() ect. Information
        unbearbeitet in Roh-Daten zurück.
        """
        if self.dbtyp == "adodb":
            SQLcommand = (
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_NAME = '$$%s';"
            ) % table_name
        elif self.dbtyp == "sqlite":
            SQLcommand = "PRAGMA table_info($$%s);" % table_name
        else:
            SQLcommand = "SHOW FIELDS FROM $$%s;" % table_name

        if debug:
            self.request.write("-"*79)
            self.request.write("\nget_table_field_information: %s\n" % SQLcommand)

        result = self.process_statement(SQLcommand)
        if debug:
            self.request.write("Raw result: %s\n" % result)
            self.request.write("-"*79)
            self.request.write("\n")
        return result

    def get_table_fields(self, table_name, debug=False):
        """
        Liefert nur die Tabellen-Feld-Namen zurück
        """
        field_information = self.get_table_field_information(table_name, debug)

        if self.dbtyp == "adodb":
            return field_information
        elif self.dbtyp == "sqlite":
            key = "name"
        else:
            key = "Field" # MySQL

        result = []
        for column in field_information:
            result.append(column[key])
        return result

    def exist_table_name(self, table_name):
        """ ݢerpr��� die existens eines Tabellen-Namens """
        for line in self.table_names():
            if line[0] == table_name:
                return True
        return False

    def encode_sql_results(self, sql_results, codec="UTF-8"):
        """
        encodiert unicode Ergebnisse eines SQL-select-Aufrufs
        """
        post_error = False
        for line in sql_results:
            for k,v in line.iteritems():
                if type(v)!=unicode:
                    continue
                try:
                    line[k] = v.encode(codec)
                except Exception, e:
                    if not post_error:
                        # Fehler nur einmal anzeigen
                        self.request.write(
                            "decode_sql_results() error in line %s: %s\n" % (
                                line, e
                            )
                        )
                        post_error = True
        return sql_results

    #_________________________________________________________________________

    def dump_table(self, tablename):
        result = self.select(select_items= "*", from_table= tablename)
        self.dump_select_result(result, info="dump table '%s'" % tablename)

    def dump_select_result(self, result, info="dumb select result"):
        self.request.write("*** %s ***\n" % info)
        for i, line in enumerate(result):
            self.request.write("%s - %s\n" % (i, line))

    def debug_command(self, methodname):
        self.request.write("-"*79)
        self.request.write("\ndb.%s - Debug:\n" % methodname)
        self.request.write("last SQL statement:\n")
        self.request.write("%s\n" % str(self.cursor.last_statement))
        self.request.write("-"*79)
        self.request.write("\n")


class ConnectionError(Exception):
    pass











#_____________________________________________________________________________
# Ein quasi billig Unit-Test:

if __name__ == "__main__":
    #~ import cgitb;cgitb.enable()
    #~ print "Content-type: text/html; charset=utf-8\r\n"
    #~ print "<pre>"

    dbtyp="sqlite"
    databasename=":memory:"
    db = SQL_wrapper(sys.stdout, dbtyp, databasename)

    print "dbtyp.......:", dbtyp
    print "databasename:", db.databasename
    print "paramstyle..:", db.paramstyle
    print "placeholder.:", db.placeholder

    print "\n\ndb.get_tables():", db.get_tables()

    if dbtyp == "sqlite":
        SQLcommand = (
            "CREATE TABLE $$TestTable ("
            "id INTEGER PRIMARY KEY,"
            "data1 VARCHAR(50) NOT NULL,"
            "data2 VARCHAR(50) NOT NULL"
            ");"
        )
    elif dbtype == "mysql":
        SQLcommand = (
            "CREATE TABLE $$TestTable ("
            "id INT( 11 ) NOT NULL AUTO_INCREMENT,"
            "data1 VARCHAR( 50 ) NOT NULL,"
            "data2 VARCHAR( 50 ) NOT NULL,"
            "PRIMARY KEY ( id )"
            ") COMMENT = 'Temporary test table';"
        )

    print "\n\nCreat a temporary test table - execute SQL-command directly...",
    db.cursor.execute(SQLcommand)
    db.commit()
    print "OK"


    print "\n\ndb.get_tables()-Test:",
    tables = db.get_tables()
    if not 'TestTable' in tables:
        print "ERROR:", tables
    else:
        print "OK:", tables


    print "\n\ndb.get_table_fields()-Test:",
    table_fields = db.get_table_fields("TestTable")
    if table_fields != ['id', 'data1', 'data2']:
        print "ERROR!"
        print "Table fields not correct:"
        print "should be: ['id', 'data1', 'data2']"
        print "is: ", table_fields
    else:
        print "OK:", table_fields


    print "\n\nSQL-insert Function:"
    db.insert(
        table = "TestTable",
        data  = { "data1" : "Value A 1", "data2" : "Value A 2" },
        debug = True
    )
    print "cursor.lastrowid:", db.cursor.lastrowid


    print "\n\nadds a new value:"
    db.insert(
        table = "TestTable",
        data  = { "data1" : "Value B 1", "data2" : "Value B 2" },
        debug = True
    )
    print "cursor.lastrowid:", db.cursor.lastrowid


    print "\n\nSQL-select Function (db.select):"
    result = db.select(
        select_items    = ["id","data1","data2"],
        from_table      = "TestTable",
        where           = ("data1","Value B 1"),
        debug=1
    )
    db.dump_select_result(result)
    if result == [{'data1': u'Value B 1', 'id': 2, 'data2': u'Value B 2'}]:
        print "OK"
    else:
        print "ERROR!"


    print "\n\ndelete the value with id=1:"
    db.delete(
        table = "TestTable",
        where = ("id",1),
        limit = 1,
        debug = True
    )
    print "cursor.lastrowid:", db.cursor.lastrowid

    db.dump_table("TestTable")

    print "\n\nUpdate item (db.update)."
    db.update(
        table   = "TestTable",
        data    = {"data1" : "NewValue1!"},
        where   = ("id",2),
        debug = True
    )
    print "cursor.lastrowid:", db.cursor.lastrowid

    print "\n\nSee all values via SQL '*'-select and ordet it by 'id':"
    result = db.select(
        select_items    = ["id","data1","data2"],
        from_table      = "TestTable",
    )
    db.dump_select_result(result)
    old_values = [{'data1': 'NewValue1!', 'id': 2, 'data2': 'Value B 2'}]
    print "\nCheck SQL:",
    if result != old_values:
        print "ERROR: Result not right!"
    else:
        print "OK, Data are as assumed."

    db.commit() # Vorherigen Aktionen committen
    print "\n\nTest Transaction:"
    db.insert("TestTable", {"data1": "tranceact1", "data2": "1"})
    id1 = db.cursor.lastrowid
    db.insert("TestTable", {"data1": "tranceact2", "data2": "2"})
    id2 = db.cursor.lastrowid
    db.delete(
        table = "TestTable",
        where = ("id",id1),
    )
    db.update(
        table   = "TestTable",
        data    = {"data1": "tranceact3"},
        where   = ("id",id2)
    )
    result = db.select(
        select_items    = "*",
        from_table      = "TestTable",
        order           = ("id","ASC"),
    )
    db.dump_select_result(result)
    db.rollback() # Alle letzten Befehle rückgängig machen
    result = db.select(
        select_items    = "*",
        from_table      = "TestTable",
        order           = ("id","ASC"),
    )
    db.dump_select_result(result)
    print "\nCheck SQL:",
    if result != old_values:
        print "ERROR: Result not right!"
    else:
        print "OK, Data are as assumed."


    print "\n\nDelete the temporary test Table."
    db.cursor.execute("DROP TABLE $$TestTable")


    print "\n\ndb.get_tables():", db.get_tables()


    print "\n\nClose SQL-connection...",
    db.close()
    print "OK"

    #~ print "<pre>"
















