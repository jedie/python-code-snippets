#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Erweitert den SQL-Wrapper mit speziellen PyDown-DB-Zugriffsmethoden
"""


import time


# SQL-Wrapper mit einfachen Statement-Generator
from database import SQL_wrapper




class PyDownDB(SQL_wrapper):
    """
    Bringt durch erben spezielle Methoden zum db-Zugriff in
    den SQL-Wrapper ein
    """

    #_________________________________________________________________________
    # schreibenden zugriff auf die DB

    def log(self, type, item):
        """
        Eintrag in die Log-Tabelle machen
        """
        current_time = time.time()
        current_user = self.request.environ["REMOTE_USER"]

        if (type == "view") or (type == "browse"):
            # Filtert doppelte Einträge (z.B. beim reload)
            result = self.select(
                select_items    = ("timestamp", "username", "type", "item"),
                from_table      = "log",
                order           = ("timestamp","DESC"),
                limit           = 1,
            )[0]
            #~ self.request.echo(result)
            if (result["username"] == current_user) and \
                (result["type"] == type) and \
                (result["item"] == item) and \
                (current_time-result["timestamp"]<30):
                return

        self.insert(
            table = "log",
            data = {
                "timestamp": current_time,
                "username": current_user,
                "type": type,
                "item": item,
            }
        )
        self.commit()

    def insert_download(self, item, total_bytes, current_bytes):
        """
        Einen neuen Download eintragen
        """
        self.insert(
            table = "activity",
            data = {
                "username": self.request.environ["REMOTE_USER"],
                "item": item,
                "start_time": time.time(),
                "total_bytes": total_bytes,
                "current_time": time.time(),
                "current_bytes": current_bytes,
            }
        )
        self.commit()
        return self.cursor.lastrowid

    def update_download(self, id, current_bytes):
        """
        Updated einen download Eintrag
        """
        self.update(
            table   = "activity",
            data    = {
                "current_bytes": current_bytes,
                "current_time": time.time(),
            },
            where   = ("id",id),
        )
        self.commit()

    #_________________________________________________________________________
    # lesenden zugriff auf die DB

    def last_log(self, limit=20):
        result = self.request.db.select(
            select_items    = ("timestamp", "username", "type", "item"),
            from_table      = "log",
            order           = ("timestamp","DESC"),
            limit           = limit,
            #~ debug = True
        )
        return self.encode_sql_results(result, codec="UTF-8")

    def current_downloads(self):
        result = self.request.db.select(
            from_table      = "activity",
            select_items    = (
                "id", "username", "item", "start_time", "current_time",
                "total_bytes", "current_bytes"
            ),
            #~ where           = ("type", filter),
            order           = ("start_time","DESC"),
            #~ limit           = (1,10),
            #~ debug = True
        )
        return self.request.db.encode_sql_results(result, codec="UTF-8")



