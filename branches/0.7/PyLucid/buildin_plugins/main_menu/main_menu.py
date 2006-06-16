#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert das komplette Seitenmenü mit Untermenüs in eine Baumansicht

Das Menü wird eingebunden mit dem lucid-Tag:
<lucidTag:main_menu/>
"""

__version__="0.2"

__history__="""
v0.2
    - Anpassung an PyLucid 0.7
v0.1
    - Anpassung an colubrid 1.0
v0.0.13
    - Änderung am Aufbau des HTML
v0.0.12
    - Bug in where_filter() behoben, sodas "permit view public" wirklich
        beachtet wird
v0.0.11
    - Es werden nurnoch Seiten angezeigt, bei denen 'showlinks' gesetzt ist.
v0.0.10
    - name und title werden nun mit cgi.escape() gewandelt, damit auch
        Seitennamen wie <robots> Angezeigt werden.
    - link wird mit urllib.quote_plus(), so sind auch Sonderzeichen wie "/"
        im Seitennamen erlaubt ;)
v0.0.9
    - Neue Methode 'where_filter()' zum berücksichtigen des Rechtemanagement
v0.0.8
    - Aufteilung in menu_sub.py und menu_main.python
    - Tag <lucidTag:main_menu/> wird über den Modul_Manager gesetzt
v0.0.7
    - Einige Änderung durch neue Seiten-Addressierungs-Umstellung
v0.0.6
    - neu: sub_menu()
    - es werden <ul>,<li> usw. aus der DB (preferences) genommen
v0.0.5
    - Anpassung an index.py (Rendern der CMS-Seiten mit Python'CGIs)
    - SQL-Connection wird nun auch beendet
v0.0.4
    - Umstellung: Neue Handhabung der CGI-Daten
v0.0.3
	- Fehlerausgabe bei unbekannter 'page_name'
v0.0.2
    - Menulink mit 'title' erweitert, Link-Text ist nun 'name'
v0.0.1
    - erste Version
"""

#~ import cgitb;cgitb.enable()

# Python-Basis Module einbinden
import re, os, sys, urllib, cgi


from PyLucid.system.BaseModule import PyLucidBaseModule

class main_menu(PyLucidBaseModule):

    def __init__(self, *args, **kwargs):
        super(main_menu, self).__init__(*args, **kwargs)

        self.menulink  = (
            '<a%(style)s class="level%(level)s" '
            'href="%(link)s" title="%(title)s">%(name)s</a>'
        )

        #~ print self.menulink

        self.current_page_id  = self.session["page_id"]

        # Wird von self.create_menudata() "befüllt"
        self.menudata = []

    def lucidTag(self):
        #~ self.URLs.debug()

        # "Startpunkt" für die Menügenerierung feststellen
        parentID = self.db.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("id",self.current_page_id)
            )[0]["parent"]

        # Gibt es Untermenupunkte?
        parentID = self.check_submenu( parentID )

        # Füllt self.menudata mit allen relevanten Daten
        self.create_menudata( parentID )

        # Ebenen umdrehen, damit das Menü auch richtig rum
        # dargestellt werden kann
        self.menudata.reverse()

        # Generiert das Menü aus self.menudata
        self.make_menu()

    def where_filter( self, where_rules ):
        """
        Erweitert das SQL-where Statement um das Rechtemanagement zu
        berücksichtigen.
        Selbe Funktion ist auch bei sub_menu vorhanden
        """
        where_rules.append(("showlinks",1))
        if not self.session.has_key("isadmin") or \
                                                self.session["isadmin"]!=True:
            where_rules.append(("permitViewPublic",1))

        return where_rules

    def check_submenu( self, parentID, internal=False ):
        """
        Damit sich das evtl. vorhandene Untermenüpunkt "aufklappt" wird
        nachgesehen ob ein Menüpunkt als ParentID die aktuelle SeitenID hat.
        """
        where_filter = self.where_filter( [("parent",self.current_page_id)] )
        # Gibt es Untermenupunkte?
        result = self.db.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = where_filter,
                limit           = (0,1)
            )
        if not result:
            # Es gibt keine höhere Ebene (keine Untermenupunkte)
            return parentID
        else:
            # Als startpunkt wird die ParentID eines Untermenupunktes übergeben
            return result[0]["parent"]

    def create_menudata( self, parentID ):
        """
        Hohlt die relevanten Menüdaten aus der DB in einer Rekursiven-Schleife
        """
        # Alle Daten der aktuellen Ebene hohlen
        parents = self.db.select(
                select_items    = ["id","name","shortcut","title","parent"],
                from_table      = "pages",
                where           = self.where_filter( [("parent",parentID)] ),
                order           = ("position","ASC")
            )
        self.menudata.append( parents )

        # Hohlt die parentID, um zur nächte Ebene zurück gehen zu können
        parent = self.db.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = [ ("id",parentID) ]
            )
        if parent:
            # Unterste Ebene noch nicht erreicht -> rekursiver Aufruf
            self.create_menudata( parent[0]["parent"] )

    def make_menu(self, menulevel=0, parentname=""):
        """
        Erstellt das Menü aus self.menudata in einer Rekursiven-Schleife
        """
        # Daten der Aktuellen Menüebene
        leveldata = self.menudata[ menulevel ]

        if len(self.menudata) > (menulevel+1):
            # Es gibt noch eine höhere Menu-Ebene
            try:
                higher_level_parent = self.menudata[ menulevel+1 ][0]["parent"]
            except IndexError:
                # Aber nicht, wenn die aktuelle Seite "versteckt" ist
                higher_level_parent = False
        else:
            # Es gibt keine höhere Ebene
            higher_level_parent = False

        # Leerzeichen für das einrücken des HTML-Code
        spacer = " " * (menulevel * 2)

        # List Anfang, default: <ul>
        self.response.write(
            "%s%s\n" % (spacer, self.preferences["mainMenu"]["begin"])
        )

        for menuitem in leveldata:
            name = menuitem["name"]
            title = menuitem["title"]
            if title == None:
                title = name

            if menuitem["id"] == self.current_page_id:
                # Der aktuelle Menüpunkt ist der "angeklickte"
                CSS_style_tag = ' class="current"'
            else:
                CSS_style_tag = ""

            link = "%s/%s" % (parentname, menuitem["shortcut"])
            linkURL = self.URLs.pageLink(link)

            self.response.write(
                "%s%s\n" % (spacer, self.preferences["mainMenu"]["before"])
            )

            self.response.write(" " * ((menulevel+1) * 2))
            htmlLink = self.menulink % {
                "style"     : CSS_style_tag,
                "level"     : menulevel,
                "link"      : linkURL,
                "name"      : cgi.escape(name),
                "title"     : cgi.escape(title)
            }
            self.response.write("%s\n" % htmlLink)

            if higher_level_parent != False:
                # Generell gibt es noch eine höhere Ebene

                if menuitem["id"] == higher_level_parent:
                    # Es wurde der Menüpunkt erreicht, der das Untermenü
                    # "enthält", deswegen kommt ab hier erstmal das
                    # Untermenü rein
                    self.make_menu(menulevel+1, link)

            self.response.write(
                "%s%s\n" % (spacer, self.preferences["mainMenu"]["after"])
            )

        #~ mainMenu = {
        #   'begin': '<ul>', 'finish': '</ul>', 'after': '</li>',
        #   'currentAfter': '', 'currentBefore': '', 'before': '<li>'
        # }
        # List Ende, default: </ul>
        self.response.write(
            "%s%s\n" % (spacer, self.preferences["mainMenu"]["finish"])
        )










