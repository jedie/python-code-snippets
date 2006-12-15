#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Zeigt an, wann der nächste DEMO-reset stattfinden wird.

Last commit info:
----------------------------------
LastChangedDate: $LastChangedDate:$
Revision.......: $Rev:$
Author.........: PyLucid Team"
"""

__version__="$Rev:$"


import datetime

from PyLucid.system.BaseModule import PyLucidBaseModule

class demo_reset_time(PyLucidBaseModule):
    def lucidTag(self):
        """
        Auslesen des nächsten reset aus der DB und Anzeigen lassen
        In der DB steht der absolute Zeitpunkt des resettes, wir rechnen
        den in Minuten um und zeigen die an, ferig ;)
        """
        try:
            next_reset = self.db.select(
                select_items    = ["reset_time"],
                from_table      = "demo_data",
                limit           = 1,
            )[0]["reset_time"]
        except Exception, e:
            self.page_msg("Can't get reset time:", e)
            return

        now = datetime.datetime.now()
        # relativer Zeitpunkt errechnen:
        next = next_reset - now 
        
        msg = (
            '<p title="absolute time: %s">Next reset in %s</p>' 
        ) % (next_reset, next)
        self.response.write(msg)
