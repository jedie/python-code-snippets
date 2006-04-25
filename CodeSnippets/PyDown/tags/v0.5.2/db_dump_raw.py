#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Dumps all PyDown Tables
"""

import sys, time
from pysqlite2 import dbapi2 as db

databasename="SQLiteDB/PyDownSQLite.db"

conn = db.connect(databasename)
conn.text_factory = str
cursor = conn.cursor()

print "databasename:", databasename
print "paramstyle..:", db.paramstyle


cursor.execute("SELECT tbl_name FROM sqlite_master;")
tablenames = [i[0] for i in cursor.fetchall()]
print tablenames

print "-"*79

dbStructure = {}
for tablename in tablenames:
    print "Table: '%s'" % tablename
    cursor.execute("PRAGMA table_info(%s);" % tablename)
    columns = cursor.fetchall()
    dbStructure[tablename] = []
    for column in columns:
        columnName = column[1]
        columnTyp = column[2]
        print "%14s - %s" % (columnTyp, columnName)
        dbStructure[tablename].append(columnName)
    print

print "="*79
print "DUMP:"
print "="*79

for tablename, column in dbStructure.iteritems():
    print ">>> Table: '%s'" % tablename

    column = ", ".join(column)
    SQLcommand = "SELECT %s FROM %s;" % (column, tablename)
    print SQLcommand
    cursor.execute(SQLcommand)

    print "-"*79
    for line in cursor.fetchall():
        print line

    print

