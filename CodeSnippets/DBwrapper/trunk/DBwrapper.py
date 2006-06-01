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

__version__="0.9"

__history__="""
v0.9
    - NEU: get_tableDict()
        Select-Abfrage mit Index-Basierende-Ergebniss-Dict
v0.8.1
    - neu unittestDBwrapper.py ;)
v0.8
    - Es gibt nun eine encoding-Angabe, damit alle String als Unicode zurück
        geliefert werden. Ist allerdings nur mit MySQLdb getestet!!!
v0.7
    - Die connect-Methode wird nun nicht mehr automatisch aufgerufen.
    - Die Connection-Parameter müßen nun explizit zur verwendeten dbapi passen!
    - Für jeder Datenbanktyp (MySQL, SQLite) gibt es eine eigene connect-Methode.
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
import sys, codecs


debug = False
#~ debug = True


class Database(object):
    """
    Klasse, die nur allgemeine SQL-Funktionen beinhaltet
    """
    def __init__(self, encoding="utf8"):
        # Zum speichern der letzten SQL-Statements (evtl. für Fehlerausgabe)
        self.last_statement = None

        self.encoding = encoding
        self.unicode_decoder = codecs.getdecoder(encoding)
        self.unicode_encoder = codecs.getencoder(encoding)
        self.dbtyp = None
        self.tableprefix = ""

    def connect_mysqldb(self, *args, **kwargs):
        self.dbtyp = "MySQLdb"

        try:
            import MySQLdb as dbapi
        except ImportError, e:
            msg  = "MySQLdb import error! Modul "
            msg += '<a href="http://sourceforge.net/projects/mysql-python/">'
            msg += 'python-mysqldb</a> not installed??? [%s]' % e
            raise ImportError(msg)

        self.dbapi = dbapi
        self._setup_paramstyle(dbapi.paramstyle)

        try:
            self.conn = WrappedConnection(
                dbapi.connect(*args, **kwargs),
                    #~ host    = host,
                    #~ user    = username,
                    #~ passwd  = password,
                    #~ db      = self.databasename,
                #~ ),
                placeholder = self.placeholder,
                unicode_decoder = self.unicode_decoder,
                unicode_encoder = self.unicode_encoder,
                prefix = self.tableprefix,
            )
        except Exception, e:
            msg = "Can't connect to DB"
            try:
                if e[1].startswith("Can't connect to local MySQL server through socket"):
                    msg += ", probably the server '%s' is wrong!" % host
            except IndexError:
                pass
            msg += " [%s]\n - " % e
            msg += "connect method args...: %s\n - " % str(args)
            msg += "connect method kwargs.: %s" % str(kwargs)
            raise ConnectionError(msg)

        self.cursor = self.conn.cursor()

        # FIXME - Funktioniert das in allen Situationen???
        #~ try:
        self.cursor.execute('set character set ?;', (self.encoding,))
        #~ except:
            #~ pass
        #~ self.cursor.execute('set names utf8;')

        try:
            # Autocommit sollte immer aus sein!
            # Geht aber nur bei bestimmten MySQL-Datenbank-Typen!
            self.conn.autocommit(False)
        except:
            pass


    def connect_sqlite(self, *args, **kwargs):
        self.dbtyp = "sqlite"
        try:
            from pysqlite2 import dbapi2 as dbapi
        except ImportError, e:
            msg  = "PySqlite import error: %s\n" % e
            msg += 'Modul <a href="http://pysqlite.org">pysqlite-mysqldb</a>\n'
            msg += " not installed???"
            raise ImportError(msg)

        self.dbapi = dbapi
        self._setup_paramstyle(dbapi.paramstyle)

        try:
            self.conn = WrappedConnection(
                dbapi.connect(*args, **kwargs),
                placeholder = self.placeholder,
                unicode_decoder = self.unicode_decoder,
                unicode_encoder = self.unicode_encoder,
                prefix = self.tableprefix,
            )
        except Exception, e:
            import os
            msg = "Can't connect to SQLite-DB (%s)\n - " % e
            msg += "check the write rights on '%s'\n - " % os.getcwd()
            msg += "connect method args...: %s\n - " % str(args)
            msg += "connect method kwargs.: %s" % str(kwargs)
            raise ConnectionError(msg)

        self.cursor = self.conn.cursor()

        self.conn.text_factory = str


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

    def __init__(
        self, cnx, placeholder, unicode_decoder, unicode_encoder, prefix=''
        ):

        self.cnx = cnx
        self.placeholder = placeholder
        self._unicode_decoder = unicode_decoder
        self._unicode_encoder = unicode_encoder
        self.prefix = prefix

    def cursor(self):
        return IterableDictCursor(
            self.cnx, self.placeholder, self._unicode_decoder,
            self._unicode_encoder, self.prefix
        )

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

    def __init__(
        self, cnx, placeholder, unicode_decoder, unicode_encoder, prefix
        ):

        self._cursor = cnx.cursor()
        self._placeholder = placeholder
        self._unicode_decoder = unicode_decoder
        self._unicode_encoder = unicode_encoder
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
            temp = []
            for item in values:
                if type(item) == unicode:
                    try:
                        item = self._unicode_encoder(item, 'strict')[0]
                    except UnicodeError:
                        item = self._unicode_encoder(item, 'replace')[0]
                        sys.stderr.write("Unicode encode Error!") #FIXME
                temp.append(item)

            temp = tuple(temp)
            args.append(temp)

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
            if isinstance(item, str):
                try:
                    item = self._unicode_decoder(item, 'strict')[0]
                except UnicodeError:
                    item = self._unicode_decoder(item, 'replace')[0]
                    sys.stderr.write("Unicode decode Error!") #FIXME
            result[col[0]] = item
        return result

    def raw_fetchall(self):
        return self._cursor.fetchall()

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

    def __init__(self, outObject, *args, **kwargs):
        super(SQL_wrapper, self).__init__(*args, **kwargs)
        self.outObject = outObject

    def process_statement(self, SQLcommand, SQL_values = ()):
        """ kombiniert execute und fetchall """
        #~ self.outObject("DEBUG:", SQLcommand)
        try:
            self.cursor.execute(SQLcommand, SQL_values)
        except Exception, e:
            msg  = "execute Error: %s\n --- " % e
            msg += "SQL-command: %s\n --- " % SQLcommand
            msg += "SQL-values: %s" % str(SQL_values)
            raise Exception(msg)

        #~ try:
        result = self.cursor.fetchall()
        #~ except Exception, e:
            #~ msg = "fetchall '%s': %s --- SQL-command: %s --- SQL-values: %s" % (
                #~ e.__doc__, e, SQLcommand, SQL_values
            #~ )
            #~ raise Exception, msg

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
        if debug: self.debug_command("insert", result)
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
        if debug: self.debug_command("update", result)
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
        SQLcommand = "SELECT "
        if isinstance(select_items, str):
            SQLcommand += select_items
        else:
            SQLcommand += ",".join(select_items)
        SQLcommand += " FROM $$%s" % from_table

        values = []

        if where:
            where_string, values = self._make_where(where)
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
        if debug: self.debug_command("select", result)
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

    def indexResult(self, selectDict, indexKey):
        """
        Wandelt ein select-Ergebnis-Liste in ein Dict um
        """
        result = {}
        for line in selectDict:
            index_value = line[indexKey]
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
        if self.dbtyp == "MySQLdb":
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
                        self.outObject.write(
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







