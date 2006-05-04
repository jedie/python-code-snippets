#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:list_of_new_sides />
Generiert eine Liste der "letzten Änderungen"
"""

__version__="0.2"

__history__="""
v0.2
    - Anpassung an v0.7
v0.1.1
    - Bugfix: URLs heißt das und nicht URL
v0.1.0
    - Anpassung an neuen Modul-Manager
v0.0.5
    - Anpassung an neuer Absolute-Seiten-Addressierung
v0.0.4
    - Bugfix: SQL Modul wird anders eingebunden
v0.0.3
    - Anpassung an index.py (Rendern der CMS-Seiten mit Python'CGIs)
    - SQL-Connection wird nun auch beendet
v0.0.2
    - Anpassung an neue SQL.py Version
    - Nur Seiten Anzeigen, die auch permitViewPublic=1 sind (also öffentlich)
v0.0.1
    - erste Version
"""


import cgitb;cgitb.enable()


# Python-Basis Module einbinden
import cgi, re


from PyLucid.system.BaseModule import PyLucidBaseModule


class list_of_new_sides(PyLucidBaseModule):

    def lucidTag(self):
        """
        Aufruf über <lucidTag:list_of_new_sides />
        """
        SQLresult = self.db.select(
            select_items    = [ "id", "name", "title", "lastupdatetime" ],
            from_table      = "pages",
            where           = ( "permitViewPublic", 1 ),
            order           = ( "lastupdatetime", "DESC" ),
            limit           = ( 0, 5 )
        )

        self.response.write('<ul id="ListOfNewSides">\n')

        url_entry  = '<li>%(date)s - <a href="'
        url_entry += self.URLs["link"]
        url_entry += '%(link)s">%(title)s</a></li>\n'

        for item in SQLresult:
            prelink = self.db.get_page_link_by_id(item["id"])
            linkTitle   = item["title"]

            if (linkTitle == None) or (linkTitle == ""):
                # Eine Seite muß nicht zwingent ein Title haben
                linkTitle = item["name"]

            lastupdate = self.tools.convert_date_from_sql( item["lastupdatetime"] )

            self.response.write(
                url_entry % {
                    "date"  : lastupdate,
                    "link"  : prelink,# + item["name"],
                    "title" : cgi.escape( linkTitle ),
                }
            )

        self.response.write("</ul>\n")













