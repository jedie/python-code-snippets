#!/usr/bin/python
# -*- coding: UTF-8 -*-

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

    * Erweiterung der Select Methode so das eine Abfrage mit LIKE Parameter
        gemacht werden kann. so wie:
            select * from table where feld like %suchwort%


Last commit info:
----------------------------------
$LastChangedDate: 2007-02-13 09:06:09 +0100 (Di, 13 Feb 2007) $
$Rev: 854 $
$Author: JensDiemer $

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""


import sys, codecs, time, datetime, cgi

from django.db import connection, backend

from PyLucid import settings



debug = False
#~ debug = True


# SQL Fehler in process_statement() können sehr lang werden wenn z.B. große
# Daten in die SQL Db geschrieben werden. Mit der Angabe werden die Teile der
# Ausgabe gekürzt auf die Zeichenlänge:
MaxErrorLen = 300





class Database(object):
    """
    Klasse, die nur allgemeine SQL-Funktionen beinhaltet
    """

    server_version = None
    connection_kwargs = None

    def __init__(self, encoding="utf8"):
        print "Database init"
        # Zum speichern der letzten SQL-Statements (evtl. für Fehlerausgabe)
        self.last_statement = None

        self.encoding = encoding

        self.dbtyp = settings.DATABASE_ENGINE
        self.dbapi = backend.Database
        self.tableprefix = settings.TABLE_PREFIX

        self._setup_paramstyle(backend.Database.paramstyle)

        self.conn = WrappedConnection(
            connection,
            placeholder = self.placeholder,
            prefix = self.tableprefix,
        )
        self.cursor = self.conn.cursor()

        if self.dbtyp == "mysql":
            self.setup_MySQL_warnings()
            # Version des Server feststellen
            self.setup_MySQL_version()

    def setup_MySQL_version(self):
        """
        3.23, 4.0, 4.1, 5.0, 5.1
        """
        version = self.get_db_variable("version")
        # Beispiel version ->> '4.1.15-Debian_1ubuntu5-log'

        self.RAWserver_version = version

        version = version.split("-",1)[0]   # ->> '4.1.15'
        version = version.split("_",1)[0]   # für pure Debian
        version = version.split(".")        # ->> ["4", "1", "15"]

        temp = []
        for i in version:
            try:
                temp.append(int(i))
            except ValueError:
                # Kann vorkommen, wenn z.B. die Version: v4.1.10a ist!
                pass

        version = tuple(temp)            # ->> (4, 1, 15)

        self.server_version = version

    def setup_MySQL_warnings(self):
        """
        MySQLdb gibt normalerweise nur eine Warnung aus, wenn z.B. bei einem
        INSERT die Daten für eine Spalte abgeschnitten werden (Data
        truncated for column...)
        siehe: http://dev.mysql.com/doc/refman/5.1/en/show-warnings.html

        Hiermir packen wir alle MySQLdb-Warnungen in die page_msg.
        """
        import warnings
        from MySQLdb import Warning as MySQLdbWarning

        old_showwarning = warnings.showwarning

        def showwarning(message, category, filename, lineno):
            if category == MySQLdbWarning:
                self.page_msg("%s (%s: %s - line %s)" % (
                        message, category, filename, lineno
                    )
                )
            else:
                old_showwarning(message, category, filename, lineno)

        warnings.showwarning = showwarning

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

    def raw_cursor(self):
        return self.cnx.cursor()

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

    #_________________________________________________________________________

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

    def execute(self, sql, values=(), do_prepare=True):
        assert isinstance(values, (tuple, list)), \
            "SQL value must be a tuple! Value: '%s' is type: %s" % (
                values, type(values)
            )
        if do_prepare:
            sql = self.prepare_sql(sql)

        self.last_statement = sql

        #~ try:
        self._cursor.execute(sql, values)
        #~ except Exception, e:
            #~ msg = "cursor.execute error: %s --- " % e
            #~ msg += "\nexecute_args: %s" % execute_args
            #~ raise Exception(e)

    def execute_raw(self, sql, values=()):
        assert isinstance(values, (tuple, list)), \
            "SQL value must be a tuple! Value: '%s' is type: %s" % (
                values, type(values)
            )
        sql = self.prepare_sql(sql)
        self.last_statement = sql
        cursor = connection.cursor()
        cursor.execute(sql, values)

    def fetchall_raw(self):
        return self._cursor.fetchall()

    def fetchone(self):
        row = self._cursor.fetchone()
        if not row:
            return ()
        row = self.makeDict(row)
        return row

    def fetchall(self):
        rows = self._cursor.fetchall()
        result = []
        for row in rows:
            row = self.makeDict(row)
            result.append(row)
        return result

    def makeDict(self, row):
        result = {}
        for idx, col in enumerate(self._cursor.description):
            item = row[idx]
            result[col[0]] = item
        return result

    def raw_fetchall(self):
        return self._cursor.fetchall()

    def raw_processone(self, SQLcommand, values=()):
        assert isinstance(values, (tuple, list)), \
            "SQL value must be a tuple! Value: '%s' is type: %s" % (
                values, type(values)
            )
        self.last_statement = SQLcommand
        cursor = connection.cursor()
        cursor.execute(SQLcommand, values)
        return cursor.fetchone()

    def __iter__(self):
        while True:
            row = self.fetchone()
            if not row:
                return
            yield row







#_____________________________________________________________________________
class SQL_Wrapper(Database):
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

    db_date_format = "%Y-%m-%d %H:%M:%S"
    fieldtype_cache = {}

    def __init__(self, outObject, *args, **kwargs):
        print "SQL_Wrapper init"
        super(SQL_Wrapper, self).__init__(*args, **kwargs)
        #~ super(Database, self).__init__(*args, **kwargs)
        self.outObject = outObject

    def process_statement(self, SQLcommand, SQL_values=()):
        """ kombiniert execute und fetchall """
        #~ self.outObject("DEBUG:", SQLcommand)

        assert isinstance(SQL_values, (tuple,list)), \
            "SQL value must be a tuple! Value: '%s' is type: %s" % (
                SQL_values, type(SQL_values)
            )

        #~ try:
        self.cursor.execute(SQLcommand, SQL_values)
        #~ except Exception, msg:
            #~ def escape(txt):
                #~ txt = cgi.escape(str(txt))
                #~ if len(txt)>MaxErrorLen:
                    #~ return txt[:MaxErrorLen]+"..."
                #~ return txt

            #~ msg  = "%s\n --- " % escape(msg)
            #~ msg += "SQL-command: %s\n --- " % escape(SQLcommand)
            #~ msg += "SQL-values: %s" % escape(SQL_values)
            #~ raise Exception(msg)

        #~ try:
        result = self.cursor.fetchall()
        #~ except Exception, e:
            #~ msg = "fetchall '%s': %s --- SQL-command: %s --- SQL-values: %s" % (
                #~ e.__doc__, e, SQLcommand, SQL_values
            #~ )
            #~ raise Exception, msg

        return result

    def insert(self, table, data, debug=False, autoprefix=True):
        """
        Vereinfachter Insert, per dict
        data ist ein Dict, wobei die SQL-Felder den Key-Namen im Dict
        entsprechen muss dabei werden Keys, die nicht
        in der Tabelle als Spalte vorkommt vorher rausgefiltert
        """
        #~ raise "test: %s" % self.databasename
        items  = data.keys()
        values = tuple(data.values())

        if autoprefix:
            SQLcommand = "INSERT INTO $$%s" % table
        else:
            SQLcommand = "INSERT INTO %s" % table

        SQLcommand += " (%s) VALUES (%s);" % (
            ",".join(items),
            ",".join([self.placeholder]*len(values))
        )

        result = self.process_statement(SQLcommand, values)
        if debug: self.debug_command("insert", result)
        return result

    def update(self, table, data, where, limit=False, debug=False,
                                                            autoprefix=True):
        """
        Vereinfachte SQL-update Funktion
        """
        data_keys   = data.keys()

        values      = data.values()
        values.append(where[1])
        values      = tuple(values)

        set = ",".join(["%s=%s" % (i, self.placeholder) for i in data_keys])

        if autoprefix:
            SQLcommand = "UPDATE $$%s" % table
        else:
            SQLcommand = "UPDATE %s" % table

        SQLcommand += " SET %(set)s WHERE %(where)s%(limit)s;" % {
            "set"       : set,
            "where"     : "%s=%s" % (where[0], self.placeholder),
            "limit"     : self._make_limit(limit)
        }

        result = self.process_statement(SQLcommand, values)
        if debug: self.debug_command("update", result)
        return result


    def select(self, select_items, from_table, where=None, order=None,
            group=None, limit=None, maxrows=0, how=1, debug=False,
            autoprefix=True
        ):
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

        maxrows - Anzahl der zur�gegebenen Datens嵺e, =0 alle Datens嵺e
        how     - Form der zur�gegebenen Daten. =1 -> als Dict, =0 als Tuple
        """
        SQLcommand = "SELECT "
        if isinstance(select_items, str):
            SQLcommand += select_items
        else:
            SQLcommand += ",".join(select_items)

        if autoprefix:
            SQLcommand += " FROM $$%s" % from_table
        else:
            SQLcommand += " FROM %s" % from_table

        values = []

        if where:
            where_string, values = self._make_where(where)
            SQLcommand += where_string

        if order:
            try:
                SQLcommand += " ORDER BY %s %s" % order
            except TypeError,e:
                msg = (
                    "Error in db.select() ORDER statement"
                    " (must be a tuple or List): %s"
                ) % e
                raise TypeError(msg)

        if group:
            try:
                SQLcommand += " GROUP BY %s %s" % group
            except TypeError,e:
                msg = (
                    "Error in db.select() GROUP statement"
                    " (must be a tuple or List): %s"
                ) % e
                raise TypeError(msg)

        SQLcommand += self._make_limit(limit)

        result = self.process_statement(SQLcommand, values)
        if debug: self.debug_command("select", result)

        return result

    def delete(self, table, where, limit=1, debug=False, autoprefix=True):
        """
        DELETE FROM table WHERE id=1 LIMIT 1
        """
        if autoprefix:
            SQLcommand = "DELETE FROM $$%s" % table
        else:
            SQLcommand = "DELETE FROM %s" % table

        where_string, values = self._make_where(where)

        SQLcommand += where_string
        if not self.dbtyp == "sqlite":
            # sqlite hat kein LIMIT bei DELETE, sondern nur bei SELECT
            SQLcommand += self._make_limit(limit)
        SQLcommand += ";"

        result = self.process_statement(SQLcommand, values)
        if debug: self.debug_command("delete", result)
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
            where = [where]

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
    # Spezial SELECT

    def get_db_variable(self, variable_name):
        """
        Liefert den Wert einer MySQL variable zurück. Dabei werden Zahlen
        von String nach long gewandelt.
        """
        SQLcommand = "SHOW VARIABLES LIKE %s;"
        #~ result = self.cursor.raw_processone(SQLcommand, (variable_name,))
        result = self.process_statement(SQLcommand, (variable_name,))
        try:
            variable_data = result[0]["Value"]
        except (IndexError, KeyError):
            raise IndexError(
                "SQL result contains not the variable '%s': %s" % (
                    variable_name, result
                )
            )

        try:
            variable_data = long(variable_data)
        except ValueError:
            pass

        return variable_data

    def indexResult(self, selectDict, indexKey):
        """
        Wandelt ein select-Ergebnis-Liste in ein Dict um
        """
        result = {}
        for line in selectDict:
            try:
                index_value = line[indexKey]
            except KeyError, e:
                msg = "Key %s not in dict. Available Keys: %s" % (
                    e, line.keys()
                )
                raise KeyError, msg
            result[index_value] = line
        return result

    def get_tableDict(self, select_items, index_key, table_name):
        """
            SELECT >select_items< FROM >table_name<

        Liefert einen select aller angegebenen Spalten zurück. Dabei wird
        das Ergebniss von einer Liste zu einem Dict umgeformt, sodas der
        Tabellen-Index >index_key< als Dict-Key dient.
        """

        if (not "*" in select_items) and (not index_key in select_items):
            # Der index muß immer mit abgefragt werden!
            select_items.append(index_key)

        data = self.select(select_items, table_name)
        data = self.indexResult(data, index_key)
        return data

    #_________________________________________________________________________

    def get_all_tables(self):
        """
        Liste aller Tabellennamen
        """
        names = []
        if self.dbtyp == "mysql":
            for line in self.process_statement("SHOW TABLES"):
                names.append(line.values()[0])
        elif self.dbtyp == "sqlite":
            for line in self.process_statement(
            "SELECT tbl_name FROM sqlite_master;"):
                if not line["tbl_name"] in names:
                    names.append(line["tbl_name"])
        else:
            raise TypeError, "DBtyp %s unknown" % self.dbtyp

        return names

    def get_tables(self):
        """
        Liefert alle Tabellennamen die das self.tableprefix haben
        """
        allTables = self.get_all_tables()
        tables = []
        for tablename in allTables:
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
            self.outObject.write("-"*79)
            self.outObject.write("\nget_table_field_information: %s\n" % SQLcommand)

        result = self.process_statement(SQLcommand)
        if debug:
            self.outObject.write("Raw result: %s\n" % result)
            self.outObject.write("-"*79)
            self.outObject.write("\n")
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
        """ Prüft die existens eines Tabellen-Namens """
        for line in self.table_names():
            if line[0] == table_name:
                return True
        return False

    def get_table_keys(self, tableName, debug=False):
        """
        Informationen über die Indizes der Tabelle,
        zurück kommt ein Dict welches als Key der Indize-Namen
        hat und als value die Informationen beinhaltet.
        """
        if self.dbtyp == "sqlite":
            raise NotImplemented
        elif self.dbtyp == "adodb":
            raise NotImplemented
        else: # MySQL
            SQLcommand = "SHOW KEYS FROM $$%s" % tableName

        result = {}
        for line in self.process_statement(SQLcommand):
            result[line["Key_name"]] = line

        return result

    #_________________________________________________________________________

    def dump_table(self, tablename):
        result = self.select(select_items= "*", from_table= tablename)
        self.dump_select_result(result, info="dump table '%s'" % tablename)

    def dump_select_result(self, result, info="dumb select result"):
        self.outObject.write("*** %s ***\n" % info)
        for i, line in enumerate(result):
            self.outObject.write("%s - %s\n" % (i, line))

    def debug_command(self, methodname, result=None):
        self.outObject.write("-"*79)
        self.outObject.write("<br />\n")
        self.outObject.write("db.%s - Debug:<br />\n" % methodname)
        self.outObject.write("last SQL statement:<br />\n")
        self.outObject.write("%s<br />\n" % str(self.cursor.last_statement))
        if result:
            self.outObject.write("Result:<br />\n")
            self.outObject.write("<pre>%s</pre><br />\n" % result)
        self.outObject.write("-"*79)
        self.outObject.write("<br />\n")


class ConnectionError(Exception):
    pass

class OverageMySQLServer(ConnectionError):
    """
    MySQL older than 4.1 are not supported.
    """
    pass






