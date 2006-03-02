#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Richtet die SQLite Datenbank ein.

Sollte auf der Kommandozeile ausgeführt werden!
"""

import sys

# Eigene Module
from PyDown.database import SQL_wrapper


db = SQL_wrapper(sys.stdout, dbtyp="sqlite", databasename="SQLiteDB/PyDownSQLite.db")


print "\ninstall Database\n"

print "dbtyp.......:", db.dbtyp
print "databasename:", db.databasename
print "paramstyle..:", db.paramstyle
print "placeholder.:", db.placeholder
print

table_data = {
    "activity": """CREATE TABLE $$activity (
        id INTEGER PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        item VARCHAR(254) NOT NULL,
        start_time INTEGER(11) NOT NULL,
        total_bytes INTEGER(11) NOT NULL,
        current_time INTEGER(11) NOT NULL,
        current_bytes INTEGER(11) NOT NULL
    );""",
    "log": """CREATE TABLE $$log (
        id INTEGER PRIMARY KEY,
        timestamp INTEGER(11) NOT NULL,
        username VARCHAR(50) NOT NULL,
        type VARCHAR(50) NOT NULL,
        item VARCHAR(254) NOT NULL
    );"""
}


#~ install_statements = []
class setup_sql(object):
    def __init__(self, db, table_data):
        self.delete_tables(table_data)
        self.create_tables(table_data)

    def delete_tables(self, table_data):
        table_list = db.get_tables()
        for tablename in table_data.keys():
            if tablename in table_list:
                print "Delete Table '%s'..." % tablename,
                db.cursor.execute("DROP TABLE $$%s;" % tablename)
                print "OK"

    def create_tables(self, table_data):
        for tablename, statement in table_data.iteritems():
            print "Create table '%s'..." % tablename,
            db.cursor.execute(statement)
            print "OK"



try:
    setup_sql(db, table_data)
except Exception, e:
    print "Error:", e
    print "Make rollback!"
    db.rollback()
else:
    db.commit()



print "\nget_tables():", db.get_tables()

print
print "everything ready!"