
"""
Some low level DB functions
"""

from django.db import connection
from PyLucid.settings import DATABASE_ENGINE


def get_all_tables():
    """
    returns a list of all DB table names.
    """
    cursor = connection.cursor()

    if DATABASE_ENGINE == "mysql":
        cursor.execute("SHOW TABLES")
        table_names = [i[0] for i in cursor.fetchall()]

    elif DATABASE_ENGINE == "sqlite3":
        cursor.execute("SELECT tbl_name FROM sqlite_master;")
        table_names = set([i["tbl_name"] for i in cursor.fetchall()])
        table_names = list(table_names)

    else:
        raise TypeError("database engine '%s' unknown" % DATABASE_ENGINE)

    return table_names
