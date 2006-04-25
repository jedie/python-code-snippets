#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:back_links/>
Generiert eine horizontale zurück-Linkleiste

Einzubinden über lucid-IncludeRemote-Tag:
<p id=Backlinks>
<lucidFunction:IncludeRemote>/cgi-bin/PyLucid/BackLinks.py?page_name=<lucidTag:page_name/></lucidFunction>
</p>
"""

__version__="0.0.8"

__history__="""
v0.0.8
    - Anpassung an neuen ModuleManager
    - Links werden richtig gequotet.
v0.0.7
    - Index-Link war falsch
v0.0.6
    - Tag <lucidTag:back_links/> über Modul-Manager
v0.0.5
    - Fast ganz neu geschrieben, durch Seiten-Addressierungs-Umstellung
v0.0.4
    - Anpassung an index.py (Rendern der CMS-Seiten mit Python'CGIs)
    - Umstellung: Neue Handhabung der CGI-Daten
    - SQL-Connection wird nun auch beendet
v0.0.3
    - Links werden statt mit print mit sys.stdout.write() geschrieben, damit kein Zeilenumbruch vorkommt
v0.0.2
    - Anpassung an neuer SQL.py Version
v0.0.1
    - erste Version
"""


import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import re, os, sys, cgi, urllib

indexSide = "Start"


class back_links:
    def __init__(self, request):

        # shorthands
        self.db             = request.db
        #~ self.session        = request.session
        self.preferences    = request.preferences
        self.URLs           = request.URLs
        #~ self.page_msg       = request.page_msg
        #~ self.log            = request.log

        self.indexlink = '<a href="%s">Index</a>' % (
            self.URLs["link"]
        )

        self.backlink  = '<a href="%s' % self.URLs["link"]
        self.backlink += '%(url)s">%(title)s</a>'

        self.current_page_id  = request.session["page_id"]

    def lucidTag( self ):
        "Backlinks generieren"
        if self.current_page_id == self.preferences["core"]["defaultPageName"]:
            # Die aktuelle Seite ist die Index-Seite, also auch keinen
            # indexLink generieren
            return ""

        # aktuelle parent-ID ermitteln
        parent_id = self.db.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("id",self.current_page_id)
            )[0]["parent"]

        if parent_id == 0:
            # Keine Unterseite vorhanden -> keine back-Links ;)
            return self.indexlink

        # Link-Daten aus der DB hohlen
        data = self.backlink_data( parent_id )

        self.make_links( data )

    def backlink_data( self, page_id ):
        """ Holt die Links von der aktuellen Seite bis zur Index-Seite aus der DB """
        data = []
        while page_id != 0:
            result = self.db.select(
                    select_items    = ["name","title","parent"],
                    from_table      = "pages",
                    where           = ("id",page_id)
                )[0]
            page_id  = result["parent"]
            data.append( result )

        # Liste umdrehen
        data.reverse()

        return data

    def make_links( self, data ):
        """ Generiert aus den Daten eine Link-Zeile """
        print self.indexlink

        oldurl = ""
        for link_data in data:
            url = oldurl + "/" + urllib.quote_plus( link_data["name"] )
            oldurl = url

            title = link_data["title"]
            if (title == None) or (title == ""):
                title = link_data["name"]

            print " &lt; " + self.backlink % {
                "url": url,
                "title": cgi.escape( title ),
            }







