#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Unitest für \PyLucid\system\URLs.py
"""


import sys, unittest


from DBwrapper import SQL_wrapper


# Note: You must manually edit the Host-Adress of the MySQL-Server!
MySQLserver = "localhost"
#~ MySQLserver = "192.168.6.2"


#~ debug = debug
debug = False




class testDBwrapper(unittest.TestCase):
    def setUp(self):
        self.db = SQL_wrapper(sys.stdout)
        self.db.tableprefix="unittest_"

        print "\n\nMySQL test"

        self.db.connect_mysqldb(
            host    = MySQLserver,
            user    = "UserName",
            passwd  = "Password",
            db      = "DatabaseName",
        )
        if debug:
            print "self.dbtyp.......:", self.db.self.dbtyp
            print "tableprefix.:", self.db.tableprefix
            print "paramstyle..:", self.db.paramstyle
            print "placeholder.:", self.db.placeholder


    def tearDown(self):
        try:
            print "Delete the temporary test Table."
            self.db.cursor.execute("DROP TABLE $$test_table")
            self.assertEqual(self.db.get_tables(), [])
        finally:
            print "Close SQL-connection..."
            self.db.close()


    def _create_table(self):
        # Create Table
        createTableStatement = (
            "CREATE TABLE $$test_table ("
            "id INT( 11 ) NOT NULL AUTO_INCREMENT,"
            "data1 VARCHAR( 50 ) NOT NULL,"
            "data2 VARCHAR( 50 ) NOT NULL,"
            "PRIMARY KEY ( id )"
            ") TYPE = InnoDB COMMENT = '%s Temporary test table';"
        ) % __file__
        print "Creat a temporary test table - execute SQL-command directly"
        self.db.cursor.execute(createTableStatement)
        self.db.commit()
        print "- "*40


    def test_get_tables1(self):
        print "get_tables()"
        self.assertEqual(self.db.get_tables(), [])


    def test_get_tables2(self):
        self._create_table()
        tables = self.db.get_tables()
        if debug: print tables
        self.assertEqual(tables, [u'unittest_test_table'])


    def test_table_fields(self):
        self._create_table()
        print "get_table_fields()"
        table_fields = self.db.get_table_fields("test_table")
        if debug: print table_fields
        self.assertEqual(table_fields, ['id', 'data1', 'data2'])


    def test_mysql(self):
        self._create_table()

        print "INSERT line 1"
        self.db.insert(
            table = "test_table",
            data  = { "data1" : "Value A 1", "data2" : "Value A 2" },
            debug = debug
        )
        lastrowid = self.db.cursor.lastrowid
        if debug: print "cursor.lastrowid:", lastrowid
        self.assertEqual(lastrowid, 1)


        print "INSERT line 2"
        self.db.insert(
            table = "test_table",
            data  = { "data1" : "Value B 1", "data2" : "Value B 2" },
            debug = debug
        )
        lastrowid = self.db.cursor.lastrowid
        if debug: print "cursor.lastrowid:", lastrowid
        self.assertEqual(lastrowid, 2)


        print "SELECT"
        result = self.db.select(
            select_items    = ["id","data1","data2"],
            from_table      = "test_table",
            where           = ("data1","Value B 1"),
            debug           = debug
        )
        if debug: self.db.dump_select_result(result)
        self.assertEqual(
            result,
            [{'data1': u'Value B 1', 'id': 2, 'data2': u'Value B 2'}]
        )

        print "tableDict"
        result = self.db.get_tableDict(
            select_items = ["data1","data2"],
            index_key = "id",
            table_name = "test_table",
        )
        self.assertEqual(
            result,
            {
                1L: {'data1': u'Value A 1', 'id': 1L, 'data2': u'Value A 2'},
                2L: {'data1': u'Value B 1', 'id': 2L, 'data2': u'Value B 2'}
            }
        )

        print "DELETE line 1"
        self.db.delete(
            table = "test_table",
            where = ("id",1),
            limit = 1,
            debug = debug
        )
        print "SELECT"
        result = self.db.select(
            select_items    = ["id","data1","data2"],
            from_table      = "test_table",
            #~ where           = ("data1","Value B 1"),
            debug           = debug
        )
        if debug: self.db.dump_select_result(result)
        self.assertEqual(
            result,
            [{'data1': u'Value B 1', 'id': 2, 'data2': u'Value B 2'}]
        )

        if debug:
            self.db.dump_table("test_table")

        print "UPDATE line 2"
        self.db.update(
            table   = "test_table",
            data    = {"data1" : "NewValue1!"},
            where   = ("id",2),
            debug = debug
        )
        if debug: print "cursor.lastrowid:", self.db.cursor.lastrowid
        self.db.commit()

        print "SELECT *"
        result = self.db.select(
            select_items    = ["id","data1","data2"],
            from_table      = "test_table",
        )
        if debug: self.db.dump_select_result(result)
        self.assertEqual(
            result,
            [{'data1': u'NewValue1!', 'id': 2, 'data2': u'Value B 2'}]
        )

    def test_transaction(self):
        print "Test Transaction:"
        self.db.insert("test_table", {"data1": "tranceact1", "data2": "1"})
        id1 = self.db.cursor.lastrowid
        self.db.insert("test_table", {"data1": "tranceact2", "data2": "2"})
        id2 = self.db.cursor.lastrowid
        self.db.delete(
            table = "test_table",
            where = ("id",id1),
        )
        self.db.update(
            table   = "test_table",
            data    = {"data1": "tranceact3"},
            where   = ("id",id2)
        )
        result = self.db.select(
            select_items    = "*",
            from_table      = "test_table",
            order           = ("id","ASC"),
        )
        if debug: self.db.dump_select_result(result)
        self.db.rollback() # Alle letzten Befehle rückgängig machen
        result = self.db.select(
            select_items    = "*",
            from_table      = "test_table",
            order           = ("id","ASC"),
        )
        if debug: self.db.dump_select_result(result)
        self.assertEqual(
            result,
            [{'data1': u'NewValue1!', 'id': 2, 'data2': u'Value B 2'}]
        )






def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testDBwrapper))
    return suite





if __name__ == "__main__":
    print
    print ">>> %s - Unitest:" % __file__
    print "_"*79
    unittest.main()
    sys.exit()



