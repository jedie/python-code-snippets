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
    # lesenden zugriff auf die DB

    def last_log(self, limit=20):
        result = self.select(
            select_items    = ("timestamp", "username", "type", "item"),
            from_table      = "log",
            order           = ("timestamp","DESC"),
            limit           = limit,
            #~ debug = True
        )
        return self.encode_sql_results(result, codec="UTF-8")

    def raw_current_downloads(self):
        self.clean_up_downloads()
        result = self.select(
            from_table      = "activity",
            select_items    = (
                "id", "username", "item", "start_time", "currently_time",
                "total_bytes", "currently_bytes"
            ),
            order           = ("start_time","DESC"),
        )
        return self.request.db.encode_sql_results(result, codec="UTF-8")

    def get_preference(self, type):
        result = self.select(
            from_table      = "preferences",
            select_items    = "value",
            where           = ("type",type),
        )
        try:
            return result[0]["value"]
        except KeyError, e:
            raise KeyError(
                "%s\n --- select data: %s" % (e, result)
            )

    def get_bandwith(self):
        return int(self.get_preference("bandwith"))

    #_________________________________________________________________________
    # schreibenden zugriff auf die DB

    def log(self, type, item):
        """
        Eintrag in die Log-Tabelle machen
        """
        current_time = time.time()
        current_user = self.request.environ["REMOTE_USER"]

        if (type == "view") or (type == "browse"):
            # Filtert doppelte Eintr�ge (z.B. beim reload)
            result = self.select(
                select_items    = ("timestamp", "username", "type", "item"),
                from_table      = "log",
                order           = ("timestamp","DESC"),
                limit           = 1,
            )
            try:
                result = result[0]
            except IndexError:
                pass
            else:
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
                "currently_time": time.time(),
                "currently_bytes": current_bytes,
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
                "currently_bytes": current_bytes,
                "currently_time": time.time(),
            },
            where   = ("id",id),
        )
        self.commit()

    def clean_up_downloads(self):
        """
        Löscht alte Downloads
        """
        SQLcommand = "DELETE FROM $$activity WHERE (currently_time<?);"
        timeout = time.time()-10
        self.cursor.execute(SQLcommand, (timeout,))
        self.commit()

    def set_preference(self, type, value):
        self.update(
            table   = "preferences",
            data    = {"value": value},
            where   = ("type",type),
        )

    def set_bandwith(self, bandwith):
        try:
            # Aus den POST Daten kommen nur Strings
            bandwith = int(bandwith)
        except ValueError:
            raise ValueError("Bandwith not a integer!")

        self.set_preference("bandwith", bandwith)

    #_________________________________________________________________________
    # Methoden die die Daten aufbereiten

    def current_downloads(self):
        """
        Aktuelle Daten der Downlaods mit errechneten Zusatzinformationen
        jedoch ohne Umrechnung in andere Größenordnungen!
        """
        downloads = self.raw_current_downloads()
        for i in downloads:
            i["percent"] = (float(i["currently_bytes"]) / i["total_bytes"]) * 100

            # Vergangene Zeit in Sekunden
            i["elapsed"] = i["currently_time"] - i["start_time"]

            # Geschätzte gesammt Zeit in Sekunden
            i["total"] = i["elapsed"] / i["currently_bytes"] * i["total_bytes"]

            # Geschätzte Rest Zeit in Sekunden
            i["estimated"] = i["total"] - i["elapsed"]

            # Durchsatz Bytes/Sec
            i["throughput"] = (i["currently_bytes"] / i["elapsed"])

        return downloads


    def human_readable_downloads(self):
        """
        Downloads in Menschen lesbarer Form
        """
        downloads = self.current_downloads()
        for i in downloads:
            i["percent"] = "%.1f%%" % i["percent"]
            i["throughput"] = "%s KBytes/s" % round(i["throughput"]/1024.0)

            i["elapsed"] = "%.1fMin" % float(i["elapsed"]/60)
            i["total"] = "%.1fMin" % float(i["total"]/60)
            i["estimated"] = "%.1fMin" % float(i["estimated"]/60)

            i["total_bytes"] = "%.1fMB" % float(i["total_bytes"]/1024.0/1024)
            i["currently_bytes"] = "%.1fMB" % float(i["currently_bytes"]/1024.0/1024)

            i["currently_time"] = time.strftime("%X", time.localtime(i["currently_time"]))
            i["start_time"] = time.strftime("%X", time.localtime(i["start_time"]))

        return downloads

    def human_readable_last_log(self, limit=20):
        data = self.last_log(limit)
        for line in data:
            line["timestamp"] = time.strftime("%x %X", time.localtime(line["timestamp"]))
        return data






