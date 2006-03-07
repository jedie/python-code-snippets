#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Dumps all PyDown Tables
"""

import sys, time
from PyDown.database import SQL_wrapper

dbtyp="sqlite"
databasename=":memory:"
databasename="SQLiteDB/PyDownSQLite.db"
db = SQL_wrapper(sys.stdout, dbtyp, databasename)

print "dbtyp.......:", db.dbtyp
print "databasename:", db.databasename
print "paramstyle..:", db.paramstyle
print "placeholder.:", db.placeholder

tables = db.get_tables()
print "\nget_tables():", tables

for table in tables:
    print "-"*79
    db.dump_table(table)