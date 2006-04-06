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
        return result
        return self.encode_sql_results(result, codec="UTF-8")

    #_________________________________________________________________________

    def raw_current_downloads(self):
        return self.raw_current_activity("downloads")

    def raw_current_uploads(self):
        return self.raw_current_activity("uploads")

    def raw_current_activity(self, tableName):
        result = self.select(
            from_table      = tableName,
            select_items    = (
                "id", "username", "item", "start_time", "currently_time",
                "total_bytes", "currently_bytes"
            ),
            order           = ("start_time","DESC"),
        )
        return self.encode_sql_results(result, codec="UTF-8")

    #_________________________________________________________________________

    def upload_count(self):
        return self.activity_count("uploads")

    def download_count(self):
        return self.activity_count("downloads")

    def activity_count(self, tableName):
        """ Anzahl der aktuellen Up-/Downloads """
        self.clean_up_activity(tableName)
        result = self.select(
            from_table      = tableName,
            select_items    = "id",
        )
        return len(result)

    #_________________________________________________________________________

    def get_download_blocksize(self, sleep_sec):
        """
            2048 0.1 -> 20KB/s
            20KB/s / Anzahl * (1024*0.1) = 2000
        """
        bandwith = self.available_bandwith()

        blocksize = bandwith * 1024.0 * sleep_sec
        return int(blocksize)

    def available_bandwith(self):
        bandwith = self.get_bandwith()
        download_count = self.download_count()

        if download_count == 0:
            return bandwith
        else:
            return float(bandwith) / download_count

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
        """ Aktuelle Bandbreite in KB/s """
        return int(self.get_preference("bandwith"))

    def last_users(self, spaceOfTime=30*60):
        result = set()

        # User die gerade Download machen
        usernames = self.select(
            from_table      = "downloads",
            select_items    = ("username",),
        )
        usernames = self.encode_sql_results(usernames, codec="UTF-8")
        for user in usernames:
            result.add(user["username"])

        # Usernamen aus der LOG-Tabelle
        SQLcommand = "SELECT username FROM $$log WHERE (timestamp>?);"
        spaceOfTime = time.time()-spaceOfTime
        usernames = self.process_statement(SQLcommand, (spaceOfTime,))
        usernames = self.encode_sql_results(usernames, codec="UTF-8")
        for user in usernames:
            result.add(user["username"])

        return list(result)

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
                    (result["item"] == item):# and \
                    #~ (current_time-result["timestamp"]<30):
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

    #_________________________________________________________________________

    def insert_download(self, item, total_bytes, current_bytes):
        """
        Einen neuen Download eintragen
        """
        return self.insert_activity(
            "downloads", item, total_bytes, current_bytes
        )

    def insert_upload(self, item, total_bytes, current_bytes):
        """
        Einen neuen Upload eintragen
        """
        return self.insert_activity(
            "uploads", item, total_bytes, current_bytes
        )

    def insert_activity(self, tableName, item, total_bytes, current_bytes):
        """
        Trägt ein Download oder Upload ein und liefert die ID zurück
        """
        self.insert(
            table = tableName,
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

    #_________________________________________________________________________

    def update_download(self, id, current_bytes):
        """
        Updated einen download Eintrag
        """
        self.update_activity("downloads", id, current_bytes)

    def update_upload(self, id, current_bytes):
        """
        Updated einen download Eintrag
        """
        self.update_activity("uploads", id, current_bytes)

    def update_activity(self, tableName, id, current_bytes):
        self.update(
            table   = tableName,
            data    = {
                "currently_bytes": current_bytes,
                "currently_time": time.time(),
            },
            where   = ("id",id),
        )
        self.commit()

    #_________________________________________________________________________

    def finished_upload(self, id):
        db.delete(
            table = "uploads",
            where = ("id",id),
        )

    #_________________________________________________________________________

    def clean_up_activity(self, tabelName):
        SQLcommand = "DELETE FROM $$%s WHERE (currently_time<?);" % tabelName
        timeout = time.time()-10
        self.cursor.execute(SQLcommand, (timeout,))
        self.commit()

    #_________________________________________________________________________

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

    def current_uploads(self):
        return self.current_activity("uploads")

    def current_downloads(self):
        return self.current_activity("downloads")

    def current_activity(self, tableName):
        """
        Aktuelle Daten der Up-/Downlaods mit errechneten Zusatzinformationen
        jedoch ohne Umrechnung in andere Größenordnungen!
        """
        items = self.raw_current_activity(tableName)
        for i in items:
            i["percent"] = (float(i["currently_bytes"]) / i["total_bytes"]) * 100

            # Vergangene Zeit in Sekunden
            i["elapsed"] = i["currently_time"] - i["start_time"]

            # Geschätzte gesammt Zeit in Sekunden
            try:
                i["total"] = i["elapsed"] / i["currently_bytes"] * i["total_bytes"]
            except ZeroDivisionError:
                i["total"] = 9999

            # Geschätzte Rest Zeit in Sekunden
            i["estimated"] = i["total"] - i["elapsed"]

            # Durchsatz Bytes/Sec
            try:
                i["throughput"] = (i["currently_bytes"] / i["elapsed"])
            except ZeroDivisionError:
                i["throughput"] = 0

        return items


    def human_readable_uploads(self):
        return self.human_readable_activity(self.current_uploads())

    def human_readable_downloads(self):
        return self.human_readable_activity(self.current_downloads())

    def human_readable_activity(self, items):
        """
        Up-/Downloads in Menschen lesbarer Form
        """
        for i in items:
            i["percent"] = "%.1f%%" % i["percent"]
            i["throughput"] = "%s KBytes/s" % round(i["throughput"]/1024.0)

            i["elapsed"] = "%.1fMin" % float(i["elapsed"]/60)
            i["total"] = "%.1fMin" % float(i["total"]/60)
            i["estimated"] = "%.1fMin" % float(i["estimated"]/60)

            i["currently_time"] = time.strftime("%X", time.localtime(i["currently_time"]))
            i["start_time"] = time.strftime("%X", time.localtime(i["start_time"]))

        return items

    def human_readable_last_log(self, limit=20):
        try:
            data = self.last_log(limit)
            for line in data:
                line["timestamp"] = time.strftime("%x %X", time.localtime(line["timestamp"]))
            return data
        except Exception, e:
            msg = "Can't create log-Data: %s" % e
            self.request.write(msg)
            return ""






