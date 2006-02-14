#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

"""
SQL-Statements Wrapper

Sammlung von Methoden fÃ¼r grundlegenden SQL-Statements:
    * SELECT
    * INSERT
    * UPDATE
    * DELETE

ZusÃ¤tzlich ein paar Allgemeine Information Methoden.
"""

__version__="0.1"

__history__="""
v0.1
    - erste Release nach aufteilung
    - Allgemeine History nach __init__ verschoben
"""

from PyLucid.system.db.database import Database

debug = False

class SQL_wrapper(Database):

    def __init__(self, *args):
        super(SQL_wrapper, self).__init__(*args)

    def fetchall(self, SQLcommand, SQL_values = ()):
        """ kombiniert execute und fetchall """
        self.last_SQLcommand = SQLcommand
        self.last_SQL_values = SQL_values
        try:
            self.cursor.execute(SQLcommand, SQL_values)
        except Exception, e:
            raise Exception(
                "execute Error: %s --- SQL-command: %s --- SQL-values: %s" % (
                e, SQLcommand, SQL_values
                )
            )
        try:
            result = self.cursor.fetchall()
        except Exception, e:
            raise Exception(
                "fetchall Error: %s --- SQL-command: %s --- SQL-values: %s" % (
                e, SQLcommand, SQL_values
                )
            )

        return result


    def get_tables(self):
        """
        Liefert alle Tabellennamen die das self.tableprefix haben
        """
        tables = []
        for table in self.fetchall("SHOW TABLES"):
            tablename = table.values()[0]
            if tablename.startswith(self.tableprefix):
                tables.append(tablename)
        return tables


    def insert(self, table, data, debug=False):
        """
        Vereinfachter Insert, per dict
        data ist ein Dict, wobei die SQL-Felder den Key-Namen im Dict
        entsprechen muß, dabei werden Keys, die nicht
        in der Tabelle als Spalte vorkommt vorher rausgefiltert
        """
        # Nicht vorhandene Tabellen-Spalten aus dem Daten-Dict löschen
        field_list = self.get_table_fields(table)
        if debug:
            print "field_list:", field_list
        index = 0
        for key in list(data.keys()):
            if not key in field_list:
                del data[key]
            index += 1

        items  = data.keys()
        values = tuple(data.values())

        SQLcommand = "INSERT INTO $$%(table)s ( %(items)s ) VALUES ( %(values)s );" % {
                "table"         : table,
                "items"         : ",".join( items ),
                "values"        : ",".join( ["%s"]*len(values) ) # Platzhalter für SQLdb-escape
            }

        if debug: debug_command("insert", SQLcommand, values)

        return self.fetchall(SQLcommand, values)


    def update(self, table, data, where, limit=False, debug=False):
        """
        Vereinfachte SQL-update Funktion
        """
        data_keys   = data.keys()

        values      = data.values()
        values.append(where[1])
        values      = tuple(values)

        SQLcommand = "UPDATE $$%(table)s SET %(set)s WHERE %(where)s %(limit)s;" % {
                "table"     : table,
                "set"       : ",".join( [str(i)+"=%s" for i in data_keys] ),
                "where"     : where[0] + "=%s",
                "limit"     : self._make_limit(limit)
            }

        if debug: debug_command("update", SQLcommand, values)

        return self.fetchall(SQLcommand, values)


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

        maxrows - Anzahl der zurückgegebenen Datensätze, =0 alle Datensätze
        how     - Form der zurückgegebenen Daten. =1 -> als Dict, =0 als Tuple
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

        if debug: debug_command("select", SQLcommand, values)

        return self.fetchall(SQLcommand, values)

    def delete(self, table, where, limit=1, debug=False):
        """
        DELETE FROM table WHERE id=1 LIMIT 1
        """
        SQLcommand = "DELETE FROM $$%s" % table

        where_string, values = self._make_where(where)

        SQLcommand += where_string
        SQLcommand += self._make_limit(limit)

        if debug: debug_command("delete", SQLcommand, values)

        return self.fetchall(SQLcommand, values)

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
            where_string.append( item[0] + "=%s" )
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

    #_________________________________________________________________________

    def get_table_field_information(self, table_name, debug=False):
        """
        Liefert "SHOW FIELDS"-Information in Roh-Daten zurÃ¼ck
        """
        if self.dbTyp == "adodb":
            SQLcommand = (
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_NAME = '$$%s';"
            ) % table_name
        else:
            SQLcommand = "SHOW FIELDS FROM $$%s;" % table_name

        if self.debug or debug:
            self.request.echo("-"*80)
            self.request.echo("get_table_field_information: %s" % SQLcommand)

        result = self.fetchall(SQLcommand)
        if self.debug or debug:
            self.request.echo("result: %s" % result)
        return result

    def get_table_fields(self, table_name):
        """
        Liefert nur die Tabellen-Feld-Namen zurÃ¼ck
        """
        field_information = self.get_table_field_information(table_name)

        if self.dbTyp == "adodb":
            return field_information

        result = []
        for column in field_information:
            result.append(column["Field"])
        return result

    def exist_table_name(self, table_name):
        """ Überprüft die existens eines Tabellen-Namens """
        self.cursor.execute( "SHOW TABLES" )
        for line in self.cursor.fetchall():
            if line[0] == table_name:
                return True
        return False

    def decode_sql_results(self, sql_results, codec="UTF-8"):
        """
        Alle Ergebnisse eines SQL-Aufrufs encoden
        """
        post_error = False
        for line in sql_results:
            for k,v in line.iteritems():
                if type(v)!=str:
                    continue
                try:
                    line[k] = v.decode(codec)
                except Exception, e:
                    if not post_error:
                        # Fehler nur einmal anzeigen
                        self.page_msg("decode_sql_results() error: %s" % e)
                        post_error = True
                        self.page_msg("line:", line)
        return sql_results

    #_________________________________________________________________________

    def dump_select_result(self, result):
        self.request.echo("*** dumb select result ***")
        for i in xrange( len(result)):
            self.request.echo("%s - %s" % (i, result[i]))

    def debug_command(self, methodname, SQLcommand, values):
        self.request.echo("-"*80)
        self.request.echo("db.%s - Debug:" % methodname)
        self.request.echo("SQLcommand.: %s" % SQLcommand)
        self.request.echo("values.....: %s" % values)
        self.request.echo("-"*80)






if __name__ == "__main__":
    import cgitb;cgitb.enable()
    print "Content-type: text/html; charset=utf-8\r\n"
    print "<pre>"

    import sys
    sys.path.insert(0,"../")
    import config # PyLucid's "config.py"

    PyLucid = {
        "config": config
    }
    db = mySQL(PyLucid)

    #~ del(db.cursor.lastrowid)

    print "SHOW TABLE STATUS:", db.cursor.execute("SHOW TABLE STATUS")
    print "SHOW TABLES:", db.cursor.execute("SHOW TABLES")

    # Prints all SQL-command:
    db.debug = True

    SQLcommand  = "CREATE TABLE $$TestTable ("
    SQLcommand += "id INT( 11 ) NOT NULL AUTO_INCREMENT,"
    SQLcommand += "data1 VARCHAR( 50 ) NOT NULL,"
    SQLcommand += "data2 VARCHAR( 50 ) NOT NULL,"
    SQLcommand += "PRIMARY KEY ( id )"
    SQLcommand += ") COMMENT = 'Temporary test table';"

    print "\n\nCreat a temporary test table - execute SQL-command directly."
    try:
        db.cursor.execute( SQLcommand )
    except Exception, e:
        print "Can't create table:", e
        #~ raise


    print "\n\nSQL-insert Function:"
    db.insert(
            table = "TestTable",
            data  = { "data1" : "Value A 1", "data2" : "Value A 2" }
        )
    print "cursor.lastrowid:", db.cursor.lastrowid

    print "\n\nadds a new value:"
    db.insert(
            table = "TestTable",
            data  = { "data1" : "Value B 1", "data2" : "Value B 2" }
        )
    print "cursor.lastrowid:", db.cursor.lastrowid

    print "\n\nSQL-select Function (db.select):"
    result = db.select(
            select_items    = ["id","data1","data2"],
            from_table      = "TestTable",
            #~ where           = ("parent",0)#,debug=1
        )
    db.dump_select_result( result )

    print "\n\ndelete a value:"
    db.delete(
            table = "TestTable",
            where = ("id",1)
        )
    print "cursor.lastrowid:", db.cursor.lastrowid

    print "\n\nUpdate an item (db.update)."
    data = { "data1" : "NewValue1!"}
    db.update(
            table   = "TestTable",
            data    = data,
            where   = ("id",1),
            limit   = 1
        )
    print "cursor.lastrowid:", db.cursor.lastrowid

    print "\n\nSee the new value (db.select):"
    result = db.select(
            select_items    = ["data1"],
            from_table      = "TestTable",
            where           = ("id",1)
        )
    db.dump_select_result( result )


    print "\n\nSee all values via SQL '*'-select and ordet it by 'id':"
    result = db.select(
            select_items    = "*",
            from_table      = "TestTable",
            order           = ("id","ASC"),
        )
    db.dump_select_result( result )

    print "\nCheck SQL:",
    if result != [{'data1': 'Value B 1', 'id': 2L, 'data2': 'Value B 2'}]:
        print "ERROR: Result not right!"
    else:
        print "OK, Data are as assumed."


    print "\n\nDelete the temporary test Table."
    db.cursor.execute( "DROP TABLE %sTestTable" % db.tableprefix )


    print "\n\nClose SQL-connection."
    db.close()

    print "<pre>"